# -*- coding: utf-8 -*-
# @Time :2022/12/11 19:35
# @Auther :Yuwenchao
# @Software : PyCharm
'''

'''
import os
import json
import networkx as nx
import pandas as pd
from my_packages import functions,ms2tools,config

def main(args):
    '''Main workflow of MSanalyst'''
    functions.create_result_folders(args)
    # ms2tools.spectral_entropy_calculating(args)
    ms2tools.ms1_match(args)
    ms2tools.ISDB_MS2_match(args)
    ms2tools.EDB_MS2_match(args)
    functions.create_subresults(args)
    ms2tools.molecular_generation(args)

def ms1search(args):
    '''
    args.query_ms1
    '''
    query = float(args.query_ms1)
    dict = {'row ID': '1', 'row m/z': query}
    query_df = pd.DataFrame([dict])
    ms2tools.ms1_match(args, queryDF=query_df)

def ms2search(args):
    '''
    args.mgf_file
    '''
    mgf_file = args.mgf_file
    spectra = functions.mgf_process(mgf_file)
    queryms1 = float(spectra.loc[0, 'pepmass'])
    dict = {'row ID': '1', 'row m/z': queryms1}
    query_df = pd.DataFrame([dict])
    ms2tools.ms1_match(args, queryDF=query_df)
    ms2tools.ISDB_MS2_match(args, queryMGF=mgf_file)
    ms2tools.EDB_MS2_match(args, queryMGF=mgf_file)

def re_networking(args):
    ms2tools.molecular_generation(args)

def mn_merging(args):
    mn1_file = args.mn1_file
    mn1_basename = os.path.basename(mn1_file).replace('.graphml', '')
    mn1_G = nx.read_graphml(mn1_file)
    node_ids = list(mn1_G.nodes())

    mn2_file = args.mn2_file
    mn2_basename = os.path.basename(mn2_file).replace('.graphml', '')
    mn2_G = nx.read_graphml(mn2_file)

    for src, dst, edge_attrs in mn1_G.edges(data=True):
        try:
            if not mn2_G.has_edge(src, dst) or (mn2_G[src][dst][0] != edge_attrs and mn2_G[src][dst][1] != edge_attrs):
                mn2_G.add_edge(src, dst, **edge_attrs)
        except:
            if not mn2_G.has_edge(src, dst) or mn2_G[src][dst][0] != edge_attrs:
                mn2_G.add_edge(src, dst, **edge_attrs)

    nx.write_graphml(mn2_G, f'{args.output}/{mn1_basename}—{mn2_basename}.graphml')

def customized_db(args):
    '''
    args.mgf_file
    args.library_info
    '''
    out_dir = args.output
    if not os.path.exists(out_dir): # check or create customed_db directory
        os.makedirs(out_dir)
    else:
        pass

    '''file upload and preprocess'''
    mgf = args.mgf_file
    feature = args.library_info
    # feature = './customed_db/Xiamenmycins_quant.xlsx'
    # mgf = './customed_db/Xiamenmycins.mgf'
    ids = functions.ex_startswith(mgf, start_txt='FEATURE_ID=')
    pepmasses = functions.ex_startswith(mgf, start_txt='PEPMASS=')
    charges = functions.ex_startswith(mgf, start_txt='CHARGE=')
    ionmodes = ['positive' if charge.endswith('+') else 'negative' for charge in charges]
    ms2s = functions.ex_spectra(mgf, start_txt='MSLEVEL=2', end_txt='END IONS')

    df = functions.df_preprocess(feature)
    smiles = df.smiles.tolist()
    compound_names = df.compound_name.tolist()

    '''customed ms1 library generating'''
    ms1_df = pd.DataFrame({
        'id': ids,
        'pepmass': pepmasses,
        'smiles': smiles
    })
    base_filename = os.path.splitext(os.path.basename(mgf))[0]
    ms1_output_filename = f"./customed_db/{base_filename}_ms1.csv"
    ms1_df.to_csv(ms1_output_filename, index=False)

    '''customed ms2 library generating'''
    ms2_data = {}
    if len(ids) != len(df): raise ValueError(f"Lengthes do not match")

    for i in range(len(ids)):
        id = ids[i]
        pepmass = pepmasses[i]
        charge = charges[i]
        smile = smiles[i]
        ionmode = ionmodes[i]
        ms2 = ms2s[i]
        compound_name = compound_names[i]

        ms2_data[id] = {
            "pepmass": pepmass,
            "charge": charge,
            "ion_mode": ionmode,
            "smiles": smile,
            "compound_name": compound_name,
            "ms2": ms2
        }

    ms2_output_filename = f"./{out_dir}/{base_filename}_ms2.json"
    with open(ms2_output_filename, 'w') as f:
        json.dump(ms2_data, f, indent=4, default=functions.arrary2list)


if __name__ == '__main__':
    args = config.args
    main(args)
