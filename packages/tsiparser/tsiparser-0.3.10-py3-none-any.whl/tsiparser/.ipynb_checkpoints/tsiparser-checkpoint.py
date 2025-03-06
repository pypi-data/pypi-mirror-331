from importlib import resources
import pickle
import os
import requests
import io

import pandas as pnd
import gempipe
import cobra

from .commons import check_gpr, check_author, check_rstring_arrow, add_reaction, get_deprecated_kos



def get_db(logger):
    
    
    logger.info("Downloading the excel file...")
    sheet_id = "1dXJBIFjCghrdvQtxEOYlVNWAQU4mK-nqLWyDQeUZqek"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    response = requests.get(url)  # download the requested file
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)   # load into memory
        exceldb = pnd.ExcelFile(excel_data)
    else:
        logger.error(f"Error during download. Please contact the developer.")
        return 1
    
    
    logger.debug("Checking table presence...")
    sheet_names = exceldb.sheet_names
    for i in ['T', 'R', 'M', 'authors']: 
        if i not in sheet_names:
            logger.error(f"Sheet '{i}' is missing!")
            return 1
        
        
    logger.debug("Loading the tables...")
    db = {}
    db['T'] = exceldb.parse('T')
    db['R'] = exceldb.parse('R')
    db['M'] = exceldb.parse('M')
    db['authors'] = exceldb.parse('authors')
    
    
    logger.debug("Checking table headers...")
    headers = {}
    headers['T'] = ['rid', 'rstring', 'tc', 'gpr_manual', 'name', 'author', 'notes']
    headers['R'] = ['rid', 'rstring', 'kr', 'gpr_manual', 'name', 'author', 'notes']
    headers['M'] = ['pure_mid', 'formula', 'charge', 'kc', 'name', 'inchikey', 'author', 'notes']
    headers['authors'] = ['username', 'first_name', 'last_name', 'role', 'mail']
    for i in db.keys(): 
        if set(db[i].columns) != set(headers[i]):
            logger.error(f"Sheet '{i}' is missing the columns {set(headers[i]) - set(db[i].columns)}.")
            return 1
        
    return db
    

    
def introduce_metabolites(logger, db, model):
    
    
    # load assets:
    with resources.path("tsiparser.assets", "idcollection_dict.pickle") as asset_path: 
        with open(asset_path, 'rb') as rb_handler:
            idcollection_dict = pickle.load(rb_handler)

    
    logger.debug("Checking duplicated metabolite IDs...")
    if len(set(db['M']['pure_mid'].to_list())) != len(db['M']): 
        pure_mids = db['M']['pure_mid'].to_list()
        duplicates = list(set([item for item in pure_mids if pure_mids.count(item) > 1]))
        logger.error(f"Sheet 'M' has duplicated metabolites: {duplicates}.")
        return 1
   
        
    # parse M:
    logger.debug("Parsing metabolites...")
    db['M'] = db['M'].set_index('pure_mid', drop=True, verify_integrity=True)
    kc_ids_modeled = set()   # account for kc codes modeled
    for pure_mid, row in db['M'].iterrows():
        
        
        # skip empty lines!
        if type(pure_mid) != str: continue
        if pure_mid.strip() == '': continue
        
        
        # parse author
        response = check_author(logger, pure_mid, row, db, 'M')
        if response == 1: return 1
        
        
        # parse formula:
        if pnd.isna(row['formula']):
            logger.error(f"Metabolite '{pure_mid}' has missing formula: '{row['formula']}'.")
            return 1
  
        
        # parse charge: 
        if pnd.isna(row['charge']): 
            logger.error(f"Metabolite '{pure_mid}' has missing charge: '{row['charge']}'.")
            return 1
        
        
        # check if 'kc' codes are real:
        if pnd.isna(row['kc']): 
            logger.error(f"Metabolite '{pure_mid}' has missing KEGG annotation (kc): '{row['kc']}'.")
            return 1
        kc_ids = row['kc'].split(';')
        kc_ids = [i.strip() for i in kc_ids]
        for kc_id in kc_ids:
            if kc_id == 'CXXXXX':  # not in KEGG; could be knowledge gap (e.g. methyl group acceptor in R10404)
                logger.debug(f"Metabolite '{pure_mid}' is not in KEGG ('{kc_id}')!")
                continue  
            if kc_id not in idcollection_dict['kc']:
                logger.error(f"Metabolite '{pure_mid}' has invalid KEGG annotation (kc): '{kc_id}'.")
                return 1
            if kc_id in kc_ids_modeled:
                logger.error(f"KEGG annotation (kc) '{kc_id}' used in metabolite '{pure_mid}' is duplicated.")
                return 1
            if kc_id != 'CXXXXX':
                kc_ids_modeled.add(kc_id)
            
            
        # check the existance of the inchikey
        if pnd.isna(row['inchikey']): 
            logger.error(f"Metabolite '{pure_mid}' has missing inchikey: '{row['inchikey']}'.")
            return 1
        # check inchikey format:
        if len(row['inchikey']) != 27 or row['inchikey'][14] != '-' or row['inchikey'][25] != '-':
            logger.error(f"Metabolite '{pure_mid}' has badly formatted inchikey: '{row['inchikey']}'.")
            return 1
        
        
        # add metabolite to model
        m = cobra.Metabolite(f'{pure_mid}_c')
        model.add_metabolites([m])
        m = model.metabolites.get_by_id(f'{pure_mid}_c')
        m.name = row['name'].strip()
        m.formula = row['formula']
        m.charge = row['charge']
        m.compartment='c'
        # add kc annotations to model
        m.annotation['kegg.compound'] = kc_ids
        
        
    return model
    
    
    
def introduce_reactions(logger, db, model): 
    
    
    # load assets:
    with resources.path("tsiparser.assets", "idcollection_dict.pickle") as asset_path:
        with open(asset_path, 'rb') as rb_handler:
            idcollection_dict = pickle.load(rb_handler)
    
    
    logger.debug("Checking duplicated reaction IDs...")
    if len(set(db['R']['rid'].to_list())) != len(db['R']): 
        pure_mids = db['R']['rid'].to_list()
        duplicates = list(set([item for item in pure_mids if pure_mids.count(item) > 1]))
        logger.error(f"Sheet 'R' has duplicated reactions: {duplicates}.")
        return 1
    
        
    # parse R:
    logger.debug("Parsing reactions...")
    db['R'] = db['R'].set_index('rid', drop=True, verify_integrity=True)
    for rid, row in db['R'].iterrows():
        
        
        # skip empty lines!
        if type(rid) != str: continue
        if rid.strip() == '': continue
        
        
        # parse author
        response = check_author(logger, rid, row, db, 'R')
        if response == 1: return 1
        
        
        # parse reaction string
        response = check_rstring_arrow(logger, row, 'R')
        if response == 1: return 1
        

        # check if 'kr' codes are real:
        if pnd.isna(row['kr']): 
            logger.error(f"Reaction '{rid}' has missing KEGG annotation (kr): '{row['kr']}'.")
            return 1
        kr_ids = row['kr'].split(';')
        kr_ids = [i.strip() for i in kr_ids]
        for kr_id in kr_ids:
            if kr_id == 'RXXXXX':  # not in KEGG; could be knowledge gap 
                logger.debug(f"Reaction '{rid}' is not in KEGG ('{kr_id}')!")
                continue  
            if kr_id not in idcollection_dict['kr']:
                logger.error(f"Reaction '{rid}' has invalid KEGG annotation (kr): '{kr_id}'.")
                return 1
        
            
        # check GPR:
        response = check_gpr(logger, rid, row, kr_ids, idcollection_dict, 'R')
        if response == 1: return 1
        
        
        # add reaction to model
        response = add_reaction(logger, model, rid, row, kr_ids, 'R')
        if response == 1: return 1
               
    
    return model
      
    
    
def introduce_transporters(logger, db, model): 
    
    
    def clone_to_external(model, mid_c, mid_e):
    
        m = cobra.Metabolite(f'{mid_e}')
        model.add_metabolites([m])
        
        m_c = model.metabolites.get_by_id(f'{mid_c}')
        m_e = model.metabolites.get_by_id(f'{mid_e}')
        m_e.compartment='e'
        
        m_e.name = m_c.name
        m_e.formula = m_c.formula
        m_e.charge = m_c.charge
        m_e.annotation = m_c.annotation
            
    
    def add_exchange_reaction(model, mid_e):
        
        r = cobra.Reaction(f'EX_{mid_e}')
        model.add_reactions([r])
        r = model.reactions.get_by_id(f'EX_{mid_e}')
        r.build_reaction_from_string(f'{mid_e} --> ')
        if mid_e in [
            # basics:
            'glc__D_e', 'nh4_e', 'pi_e', 'so4_e', 'h2o_e', 'h_e', 'o2_e', 'co2_e',
            # metals: 
            'cu2_e', 'mobd_e', 'fe2_e', 'cobalt2_e',
        ]:
            r.bounds = (-1000, 1000)
        else:
            r.bounds = (0, 1000)
    
    
    # load assets:
    with resources.path("tsiparser.assets", "idcollection_dict.pickle") as asset_path:
        with open(asset_path, 'rb') as rb_handler:
            idcollection_dict = pickle.load(rb_handler)
    
    
    # get all already inserted metabolites
    mids_parsed = [m.id for m in model.metabolites]
    rids_parsed = [r.id for r in model.reactions]
    
    
    # protons may not have an explicit transporter
    clone_to_external(model, 'h_c', 'h_e')
    mids_parsed.append('h_e')
    add_exchange_reaction(model, 'h_e')
    rids_parsed.append(f'EX_h_e')
    
    
    # parse T:
    logger.debug("Parsing transporters...")
    db['T'] = db['T'].set_index('rid', drop=True, verify_integrity=True)
    for rid, row in db['T'].iterrows():
        
        
        # skip empty lines!
        if type(rid) != str: continue
        if rid.strip() == '': continue
        
        
        # parse author
        response = check_author(logger, rid, row, db, 'T')
        if response == 1: return 1
        
        
        # parse reaction string
        response = check_rstring_arrow(logger, row, 'T')
        if response == 1: return 1

            
        # check GPR:
        response = check_gpr(logger, rid, row, None, idcollection_dict, 'T')
        if response == 1: return 1
        
        
        # get involved metabolites:
        involved_mids = row['rstring'].split(' ')
        involved_mids = [i for i in involved_mids if i not in ['-->', '<=>']]
        
        
        # the external metabolite must be already modeled as cytosolic
        for mid in involved_mids: 
            if mid.endswith('_e'):
                mid_e = mid
                mid_c = mid.rsplit('_', 1)[0] + '_c'
                if mid_c not in mids_parsed:
                    logger.error(f"{rid}: the metabolite '{mid_c}', counterpart of '{mid_e}', was not previously modeled.")
                    return 1
                
                # add external metabolite to model
                if mid_e not in mids_parsed:
                    clone_to_external(model, mid_c, mid_e)
                    mids_parsed.append(mid_e)
                    
                # add exchange reaction to model
                if f'EX_{mid_e}' not in rids_parsed:
                    add_exchange_reaction(model, mid_e)
                    rids_parsed.append(f'EX_{mid_e}')
                    
                    
        # add reaction to model
        response = add_reaction(logger, model, rid, row, None, 'T')
        if response == 1: return 1
        
    
    return model



def introduce_sinks_demands(logger, model): 
    
    # WARNING: both 'hd_un' and 'ha_un' are present
    sinks = ['apoACP', 'apocarb', 'ha_un', 'hd_un', 'thioca']
    demands = ['scp', 'amob', 'dialurate', ]
    
    
    for puremid in sinks: 
        r = cobra.Reaction(f'sn_{puremid}_c')
        model.add_reactions([r])
        r = model.reactions.get_by_id(f'sn_{puremid}_c')
        r.build_reaction_from_string(f'{puremid}_c <=> ')
        r.bounds = (-1000, 1000)
    
    
    for puremid in demands: 
        r = cobra.Reaction(f'dm_{puremid}_c')
        model.add_reactions([r])
        r = model.reactions.get_by_id(f'dm_{puremid}_c')
        r.build_reaction_from_string(f'{puremid}_c --> ')
        r.bounds = (0, 1000)
    
    
    return model



def introduce_biomass(logger, db, model): 
    
    
    biomass_dict = {
        'amino_acids': [
            'ala__L_c', 'arg__L_c', 'asn__L_c', 'asp__L_c', 'cys__L_c', 
            'gln__L_c', 'glu__L_c', 'gly_c',    'his__L_c', 'ile__L_c', 
            'leu__L_c', 'lys__L_c', 'met__L_c', 'ser__L_c', 'pro__L_c', 
            'thr__L_c', 'trp__L_c', 'tyr__L_c', 'val__L_c', 'phe__L_c'
        ],
        'ribo_nucleotides': [
            'atp_c', 'ctp_c', 'gtp_c', 'utp_c'
        ],
        'deoxyribo_nucleotides': [
            'datp_c', 'dctp_c', 'dgtp_c', 'dttp_c'
        ],
        'cofactors': [
            'accoa_c', 
            'fad_c', 'nad_c', 'nadp_c', 
            'moco_c', 'thf_c', 'thmpp_c', 'pydx5p_c', 
            'ribflv_c', 'pnto__R_c', 
            'mql8_c', # menaquinol / manaquinone (mqn8_c)
            'q8h2_c', # ubiquinol / ubiquinone (q8_c)
            'phllqol_c', # phylloquinol / phylloquinone (phllqne_c)
            'btn_c', # biotin
            'adocbl_c', # vitamin B12
            'hemeO_c', # heme O
            'pheme_c', # protoheme
            'sheme_c', # siroheme
            'fmn_c', # FMN
            'gthrd_c', # glutathione (reduced)
        ],
        'membrane_wall': [
            'pe120_c', # phosphatidyl-ethanolamine (12:0;12:0)
            'pg120_c', # phosphatidyl-glycerol (12:0;12:0)
            'clpn120_c', # cardiolipin (12:0;12:0;12:0;12:0)
            'peptido_c', # peptidoglycan 
            # 1-lysyl phosphatidylglycerol (plantarum)
            # undecaprenol (plantarum)
            # teichoic acids
            # lipoteichoic acids
            # capsular polysaccharides
        ],
        'energy_stock': [
            # glycogen
            # starch
            # PHA / PHB
        ]
    }
    
    
    rstring =           f'0.01 {" + 0.01 ".join(biomass_dict["amino_acids"])}'
    rstring = rstring + f' + 0.01 {" + 0.01 ".join(biomass_dict["ribo_nucleotides"])}'
    rstring = rstring + f' + 0.01 {" + 0.01 ".join(biomass_dict["deoxyribo_nucleotides"])}'
    rstring = rstring + f' + 0.01 {" + 0.01 ".join(biomass_dict["cofactors"])}'
    rstring = rstring + f' + 0.01 {" + 0.01 ".join(biomass_dict["membrane_wall"])}'
    rstring = rstring + f' + 0.01 atp_c + 0.01 h2o_c --> 0.01 adp_c + 0.01 h_c + 0.01 pi_c'
    
    
    r = cobra.Reaction('Biomass')
    model.add_reactions([r])
    r = model.reactions.get_by_id('Biomass')
    r.build_reaction_from_string(rstring)
    
    
    # set as objective:
    model.objective = 'Biomass'
    
    
    return model



def translate_annotate_genes(logger, model):
    
    
    # load assets:
    with resources.path("tsiparser.assets", "idcollection_dict.pickle") as asset_path:
        with open(asset_path, 'rb') as rb_handler:
            idcollection_dict = pickle.load(rb_handler)
       
    ko_to_name = idcollection_dict['ko_to_name']
    ko_to_symbols = idcollection_dict['ko_to_symbols']
    ko_to_ecs = idcollection_dict['ko_to_ecs']
    ko_to_cogs = idcollection_dict['ko_to_cogs']
    ko_to_gos = idcollection_dict['ko_to_gos']
    
    
    # translation dicts: assign to each KO a symbol that is unique in the universe model.
    ko_to_sym = {}
    sym_to_ko = {}
    cnt = 0
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        ko = g.id
        cnt += 1
        
        if ko in get_deprecated_kos():
            # if the ko is deprecated, it was not included in 'ko_to_symbols'
            ko_to_sym[ko] = ko
            sym_to_ko[ko] = ko
            continue
            
        for symbol in ko_to_symbols[ko]:  # iterate the available symbols for this KO
            if symbol not in sym_to_ko.keys():   # take the first available (not yet used)
                ko_to_sym[ko] = symbol
                sym_to_ko[symbol] = ko
                break
          
        if cnt != len(ko_to_sym):  # no symbol was assigned (symbol was already taken by another KO)
            cnt_dups = 2
            symbol = list(ko_to_symbols[ko])[0] + f'_{cnt_dups}'   # generate a new symbol
            while cnt != len(ko_to_sym):   # until a symbol is assigned
                if symbol not in sym_to_ko.keys():   # if the new symbol fits
                    ko_to_sym[ko] = symbol
                    sym_to_ko[symbol] = ko
                cnt_dups += 1
                
    
    # insert annotations
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        ko = g.id
        g.annotation['ko'] = ko
        
        if ko not in get_deprecated_kos():
            # deprecated kos are missing from these dicts
            g.name = ko_to_name[ko]
            g.annotation['symbols'] = list(ko_to_symbols[ko])
            g.annotation['ec'] = list(ko_to_ecs[ko])
            g.annotation['cog'] = list(ko_to_cogs[ko])
            g.annotation['go'] = list(ko_to_gos[ko])
        
    
        
    # finally apply translations of IDs
    translation_dict = ko_to_sym
    translation_dict['orphan'] = 'orphan'
    translation_dict['spontaneous'] = 'spontaneous'
    cobra.manipulation.rename_genes(model, translation_dict)
    
    
    return model
    


def set_up_groups(logger, model):
    
    # load assets:
    with resources.path("tsiparser.assets", "idcollection_dict.pickle") as asset_path:
        with open(asset_path, 'rb') as rb_handler:
            idcollection_dict = pickle.load(rb_handler)
       
    kr_to_maps = idcollection_dict['kr_to_maps']
    map_to_name = idcollection_dict['map_to_name']
    kr_to_mds = idcollection_dict['kr_to_mds']
    md_to_name = idcollection_dict['md_to_name']
    
    
    # define groups of available contents
    groups = {}   # mixing maps and mds
    for r in model.reactions:
        
        if 'kegg.reaction' not in r.annotation.keys():
            continue   # Biomass, exchanges, demands, sinks, transporters
        kr_ids = r.annotation['kegg.reaction']
            
        for kr_id in kr_ids:
            if kr_id == 'RXXXXX':
                continue
            
            # insert maps
            for map_id in kr_to_maps[kr_id]:
                if map_id not in groups.keys():
                    groups[map_id] = set()
                groups[map_id].add(r)
                
            # insert mds
            for md_id in kr_to_mds[kr_id]:
                if md_id not in groups.keys():
                    groups[md_id] = set()
                groups[md_id].add(r)
                
    # finally insert groups
    for group_id in groups.keys():
                
        # get group name
        if group_id.startswith('map'):
            name = map_to_name[group_id]
        if group_id.startswith('M'):
            name = md_to_name[group_id]
                    
        actual_group = cobra.core.Group(
            group_id, 
            name = name,
            members = list(groups[group_id]),
            kind = 'partonomy',
        )
        model.add_groups([actual_group])
        
        
    return model


    
def check_biosynthesis(logger, model, growth, biosynth):
    
    
    if growth: 
        
        # check production of biomass precursors: 
        logger.info("Checking biosynthesis of every biomass component...")
        
        print()
        mids = gempipe.check_reactants(model, 'Biomass')
        if mids == []: 
            print("No blocked biomass component detected!")
        print()

        
        
    if biosynth != '-':
        
        # check biosynthesis of every modeled metabolite:
        logger.info("Checking biosynthesis of every metabolite...")
        df_rows = []
        for m in model.metabolites:
            if m.id.endswith('_c'):
                binary, obj_value, status = gempipe.can_synth(model, m.id)
                df_rows.append({'mid': m.id, 'binary': binary, 'obj_value': obj_value, 'status': status})
        df_rows = pnd.DataFrame.from_records(df_rows)
        df_rows = df_rows.set_index('mid', drop=True, verify_integrity=True)
        
        # save table as excel: 
        df_rows.to_excel('biosynth.xlsx')
        logger.info(f"'{os.getcwd()}/biosynth.xlsx' created!")
        
        
        
        # focus on a particular metabolite:
        modeld_mids = [m.id for m in model.metabolites]
        if not (biosynth in modeld_mids and biosynth.endswith('_c')):
            logger.error(f"Cytosolic metabolite defined with --biosynth is not included: '{biosynth}'.")
            return 1
        
        nsol = 5   # number of solutions
        logger.info(f"Computing {nsol} gapfilling solutions for cytosolic metabolite {biosynth}...")
        gramneg = gempipe.get_universe(staining='neg')
        with model, gramneg:
            
            # mirror the medium
            gempipe.reset_growth_env(gramneg)
            for mid in ['glc__D_e', 'nh4_e', 'pi_e', 'so4_e', 'h2o_e', 'h_e', 'o2_e', 'co2_e']:
                gramneg.reactions.get_by_id(f"EX_{mid}").lower_bound = -1000
            for exr in ['EX_k_e', 'EX_mg2_e', 'EX_fe3_e', 'EX_cl_e', 'EX_ca2_e', 'EX_mn2_e', 'EX_cobalt2_e', 'EX_cu2_e', 'EX_zn2_e']:
                gramneg.reactions.get_by_id(exr).lower_bound = -1000   
            
            print()
            # perform gap-filling, solutions are shown using print()
            _ = gempipe.perform_gapfilling(model, gramneg, biosynth, nsol=nsol)
            print()
             
    
    return 0

  
    
def parse_eggnog(model, eggnog):
    
    
    eggnog = pnd.read_csv(eggnog, sep='\t', comment='#', header=None)
    eggnog.columns = 'query	seed_ortholog	evalue	score	eggNOG_OGs	max_annot_lvl	COG_category	Description	Preferred_name	GOs	EC	KEGG_ko	KEGG_Pathway	KEGG_Module	KEGG_Reaction	KEGG_rclass	BRITE	KEGG_TC	CAZy	BiGG_Reaction	PFAMs'.split('\t')
    eggnog = eggnog.set_index('query', drop=True, verify_integrity=True)
    
    
    # PART 1. get KO codes available
    kos_org = set()
    for gid, kos in eggnog['KEGG_ko'].items():
        if kos == '-': 
            continue
        kos = kos.split(',')
        kos = [i.replace('ko:', '') for i in kos]
        for ko in kos: 
            kos_org.add(ko)
            
            
    # PART 2. get reactions in the organism (even the GPR is not complete)
    # load assets:
    with resources.path("tsiparser.assets", "idcollection_dict.pickle") as asset_path: 
        with open(asset_path, 'rb') as rb_handler:
            idcollection_dict = pickle.load(rb_handler)
            
    kr_to_kos = idcollection_dict['kr_to_kos']
    krs_org = set()
    for kr, kos in kr_to_kos.items(): 
        if any([ko in kos_org for ko in kos]):
            krs_org.add(kr)
    
    
    return krs_org
    
    
    
def check_completeness(logger, model, progress, module, focus, eggnog): 
    # check KEGG annotations in the universe model to get '%' of completeness per pathway/module.
    
    
    # load assets:
    with resources.path("tsiparser.assets", "idcollection_dict.pickle") as asset_path:
        with open(asset_path, 'rb') as rb_handler:
            idcollection_dict = pickle.load(rb_handler)
            
            
    # load assets:
    with resources.path("tsiparser.assets", "summary_dict.pickle") as asset_path: 
        with open(asset_path, 'rb') as rb_handler:
            summary_dict = pickle.load(rb_handler)
            
            
    # get the reference set of kr codes (all kegg or organism specific): 
    if eggnog != '-':
        kr_uni = parse_eggnog(model, eggnog)
        kr_uni_label = "'eggnog annotation'"
    else: 
        kr_uni = idcollection_dict['kr']
        kr_uni_label = "'whole KEGG'"
    
    
    # get all the 'kr' annotations in the model
    kr_ids_modeled = set()
    for r in model.reactions: 
        if 'kegg.reaction' in r.annotation.keys():
            for kr_id in r.annotation['kegg.reaction']:
                kr_ids_modeled.add(kr_id)
    logger.info(f"Universe coverage for {kr_uni_label}: {round(len(kr_ids_modeled.intersection(kr_uni))/len(kr_uni)*100, 0)}%!")
    
    
    # get all the map / md codes:
    map_ids = set()
    md_ids = set()
    for i in summary_dict:
        map_ids.add(i['map_id'])
        for j in i['mds']:
            md_ids.add(j['md_id'])
            
            
    # check if 'focus' exist
    if focus != '-' and focus not in map_ids and focus not in md_ids:
        logger.error(f"The ID provided with --focus does not exist: {focus}.")
        return 1
    if focus.startswith('map'):
        logger.debug(f"With --focus {focus}, --module will switch to False.")
        module = False
    if focus != '-':
        missing_logger = ()
    
    
    # define some counters:
    maps_finished = set()
    maps_noreac = set()
    maps_missing = set()
    maps_partial = set()

    
    list_partials  = []
    
    
    # iterate over each map:
    for i in summary_dict:
        
        
        # get ID and name: 
        map_id = i['map_id']
        map_name_short = f"{list(i['map_name'])[0][:20]}"
        if len(list(i['map_name'])[0]) > 20: 
            map_name_short = map_name_short + '...'
        else:  # add spaces as needed: 
            map_name_short = map_name_short + ''.join([' ' for i in range(23-len(map_name_short))])
            
            
        # check if this map was (at least partially) covered:
        map_krs = set([kr for kr in i['kr_ids'] if kr in kr_uni])
        missing = map_krs - kr_ids_modeled
        present = kr_ids_modeled.intersection(map_krs)
        if focus == map_id: 
            missing_logger = (map_id, missing)

        
        if missing == set() and map_krs != set():
            maps_finished.add(map_id)
            
        elif map_krs == set():
            maps_noreac.add(map_id)
            
        elif missing == map_krs:
            maps_missing.add(map_id)
            
        elif len(missing) < len(map_krs):
            maps_partial.add(map_id)
            
            # get '%' of completeness:
            perc_completeness = len(present)/len(map_krs)*100
            perc_completeness_str = str(round(perc_completeness))   # version to be printed
            if len(perc_completeness_str)==1: 
                perc_completeness_str = ' ' + perc_completeness_str
                
            list_partials.append({
                'map_id': map_id,
                'map_name_short': map_name_short, 
                'perc_completeness': perc_completeness,
                'perc_completeness_str': perc_completeness_str,
                'present': present,
                'missing': missing,
                'md_ids': [j['md_id'] for j in i['mds']],
            })
                
            
    # order list by '%' of completness and print:
    list_partials = sorted(list_partials, key=lambda x: x['perc_completeness'], reverse=True)
    for i in list_partials:
        if progress:
            if focus=='-' or focus in i['md_ids'] or focus==i['map_id']:
                logger.info(f"{i['map_id']}: {i['map_name_short']} {i['perc_completeness_str']}% completed, {len(i['present'])} added, {len(i['missing'])} missing.")
        
        
        # get the correspondent pathway element of the 'summary_dict'
        right_item = None
        for k in summary_dict:
            if k['map_id'] == i['map_id']:
                right_item = k
                
                
        # define some counters:
        mds_completed = set()
        mds_noreac = set()
        mds_missing = set()
        mds_partial = set()


        list_partials_md  = []
        spacer = '    '


        # iterate over each module:
        for z in right_item['mds']:


            # get ID and name: 
            md_id = z['md_id']
            md_name_short = f"{list(z['md_name'])[0][:20]}"
            if len(list(z['md_name'])[0]) > 20: 
                md_name_short = md_name_short + '...'
            else:  # add spaces as needed: 
                md_name_short = md_name_short + ''.join([' ' for i in range(23-len(md_name_short))])


            # check if this module was (at least partially) covered:
            md_krs = set([kr for kr in z['kr_ids_md'] if kr in kr_uni])
            missing = md_krs - kr_ids_modeled
            present = kr_ids_modeled.intersection(md_krs)
            if focus == md_id: 
                missing_logger = (md_id, missing)
            
            
            if missing == set() and md_krs != set():
                mds_completed.add(md_id)

            elif md_krs == set():
                mds_noreac.add(md_id)

            elif missing == md_krs:
                mds_missing.add(md_id)

            elif len(missing) < len(md_krs):
                mds_partial.add(md_id)

                # get '%' of completeness:
                perc_completeness = len(present)/len(md_krs)*100
                perc_completeness_str = str(round(perc_completeness))   # version to be printed
                if len(perc_completeness_str)==1: 
                    perc_completeness_str = ' ' + perc_completeness_str

                list_partials_md.append({
                    'md_id': md_id,
                    'md_name_short': md_name_short, 
                    'perc_completeness': perc_completeness,
                    'perc_completeness_str': perc_completeness_str,
                    'present': present,
                    'missing': missing,
                })
               
            
        # order list by '%' of completness and print:
        list_partials_md = sorted(list_partials_md, key=lambda x: x['perc_completeness'], reverse=True)
        for z in list_partials_md:
            if module:
                if focus=='-' or focus==z['md_id']:
                    logger.info(f"{spacer}{z['md_id']}: {z['md_name_short']} {z['perc_completeness_str']}% completed, {len(z['present'])} added, {len(z['missing'])} missing.")
        
        
        # print summary:
        if module and focus=='-':
            logger.info(f"{spacer}Modules of {right_item['map_id']}: completed {len(mds_completed)} - partial {len(mds_partial)} - missing {len(mds_missing)} - noreac {len(mds_noreac)}")
    if focus != '-':
        logger.info(f"Missing reactions focusing on {missing_logger[0]}: {missing_logger[1]}.")
    logger.info(f"Maps: finished {len(maps_finished)} - partial {len(maps_partial)} - missing {len(maps_missing)} - noreac {len(maps_noreac)}")
            
        
    return 0        


    
def tsiparser(args, logger): 
    
    
    if args.progress==False and args.module==True: 
        logger.error(f"You cannot ask --module without --progress (see --help).")
        return 1
    
    if args.progress==False and args.focus!='-':
        logger.error(f"You cannot ask --focus without --progress (see --help).")
        return 1
    
    
    # check file structure
    db = get_db(logger)
    if type(db)==int: return 1
                                    
        
    # create the model
    model = cobra.Model('newuni')
        
    
    model = introduce_metabolites(logger, db, model)
    if type(model)==int: return 1


    model = introduce_reactions(logger, db, model)
    if type(model)==int: return 1


    model = introduce_transporters(logger, db, model)
    if type(model)==int: return 1


    model = introduce_sinks_demands(logger, model)
    if type(model)==int: return 1


    model = introduce_biomass(logger, db, model)
    if type(model)==int: return 1


    model = translate_annotate_genes(logger, model)
    if type(model)==int: return 1


    model = set_up_groups(logger, model)
    if type(model)==int: return 1
    
    
    # output the universe
    cobra.io.save_json_model(model, 'newuni.json')
    cobra.io.write_sbml_model(model, 'newuni.xml')   # groups are saved only to SBML 
    G = len([g.id for g in model.genes])
    R = len([r.id for r in model.reactions])
    M = len([m.id for m in model.metabolites])
    uM = len(set([m.id.rsplit('_', 1)[0] for m in model.metabolites]))
    bP = len([m.id for m in model.reactions.get_by_id('Biomass').reactants])
    logger.info(f"'{os.getcwd()}/newuni.json' created!")
    logger.info(f"'{os.getcwd()}/newuni.xml' created!")
    logger.info(f"Features: [G: {G}, R: {R}, M: {M}, uM: {uM}, bP: {bP}, Biomass: {round(model.slim_optimize(), 3)}]")

    
    
    response = check_biosynthesis(logger, model, args.growth, args.biosynth)
    if response==1: return 1
    
    
    response = check_completeness(logger, model, args.progress, args.module, args.focus, args.eggnog)
    if response==1: return 1

    
    return 0