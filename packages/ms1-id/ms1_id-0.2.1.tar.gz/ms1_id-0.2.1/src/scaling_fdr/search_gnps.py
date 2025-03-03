import pandas as pd
from tqdm import tqdm
import pickle
import numpy as np
from _centroid_data import centroid_spectrum_for_search
from flash_cos import FlashCos


def search_main(library, qry_df, out_name,
                mz_tol=0.05, score_cutoff=0., min_matched_peak=1, min_spec_usage=0.0):

    with open(library, 'rb') as file:
        search_eng = pickle.load(file)

    all_matches = []
    for _, row in tqdm(qry_df.iterrows(), total=qry_df.shape[0]):
        peaks = row['peaks']
        peaks = centroid_spectrum_for_search(peaks, width_da=mz_tol * 2.015)

        peaks = peaks[peaks[:, 1] > np.max(peaks[:, 1]) * 0.01]

        matching_result = search_eng.search(
            precursor_mz=float(row['Precursor_mz']),
            peaks=peaks,
            ms1_tolerance_in_da=mz_tol,
            ms2_tolerance_in_da=mz_tol,
            method="identity",
            precursor_ions_removal_da=0.5,
            noise_threshold=0.0,
            min_ms2_difference_in_da=mz_tol * 2.02,
            reverse=True
        )

        score_arr, matched_peak_arr, spec_usage_arr = matching_result['identity_search']

        # filter by matching cutoffs
        v = np.where((score_arr >= score_cutoff) &
                     (matched_peak_arr >= min_matched_peak))[0]

        matches = []
        for idx in v:
            matched = {k.lower(): v for k, v in search_eng[idx].items()}

            matches.append({
                'score': score_arr[idx],
                'matched_peak': matched_peak_arr[idx],
                'spec_usage': spec_usage_arr[idx],
                'qry_db_id': row['NIST_No'],
                'qry_name': row['Name'],
                'qry_prec_mz': row['Precursor_mz'],
                'qry_inchikey': row['InChIKey'],
                'matched_inchikey': matched.get('inchikey', ''),
                'matched_db_id': matched.get('comment', ''),
                'matched_name': matched.get('name', '')
            })

        all_matches.extend(matches)

    all_df = pd.DataFrame(all_matches)
    all_df.to_csv(f"{out_name}_results.tsv", sep='\t', index=False)


def add_nist_qry_smiles():
    # metadata from NIST20
    nist20 = pd.read_pickle('nist20_df.pkl')
    nist20['NIST_No'] = nist20['TITLE'].apply(lambda x: x.split('NIST')[1].strip())
    # dict from NIST_No to SMILES
    nist_no_to_smiles = nist20.set_index('NIST_No')['SMILES'].to_dict()

    for mode in ['k0', 'k10']:
        df = pd.read_csv(f'{mode}_results.tsv', sep='\t')

        df['qry_db_id'] = df['qry_db_id'].astype(str)
        df['qry_smiles'] = df['qry_db_id'].map(nist_no_to_smiles, na_action='ignore')

        df['qry_inchikey_14'] = df['qry_inchikey'].str[:14]
        df['matched_inchikey_14'] = df['matched_inchikey'].str[:14]

        df.to_csv(f'{mode}_results.tsv', sep='\t', index=False)


def add_ion_mode(search):
    """
    only keep rows with ion mode matched
    """
    nist20 = pd.read_csv('/Users/shipei/Documents/projects/ms2/ms2_lib/nist20/nist20/nist20.tsv',
                         sep='\t', low_memory=False)
    nist20['Ion_mode'] = nist20['Ion_mode'].str.lower()
    # dict from NIST_No to ion mode
    nist_no_to_ion_mode = nist20.set_index('NIST_No')['Ion_mode'].to_dict()

    gnps = pd.read_pickle('/Users/shipei/Documents/projects/ms1_id/data/ms2db/gnps.pkl')
    gnps['ion_mode'] = gnps['ion_mode'].str[0].str.lower()
    gnps_id_to_ion_mode_dict = dict(zip(gnps['db_id'], gnps['ion_mode']))

    df = pd.read_csv(f'{search}_results_mces.tsv', sep='\t')

    df['matched_gnps_id'] = df['matched_db_id'].apply(lambda x: x.split('=')[1].split(';')[0])  # gnps
    df['matched_ion_mode'] = df['matched_gnps_id'].map(gnps_id_to_ion_mode_dict)

    df['qry_ion_mode'] = df['qry_db_id'].map(nist_no_to_ion_mode)

    df['ion_mode_match'] = df['qry_ion_mode'] == df['matched_ion_mode']

    # save
    df.to_csv(f'{search}_results_mces.tsv', sep='\t', index=False)
    print(df['ion_mode_match'].value_counts())


if __name__ == '__main__':
    qry_df = pd.read_pickle('low_energy_nist20.pkl')

    library = '/Users/shipei/Documents/projects/ms1_id/data/gnps.pkl'
    search_main(library, qry_df, 'k0')

    library = '/Users/shipei/Documents/projects/ms1_id/data/gnps_k10.pkl'
    search_main(library, qry_df, 'k10')

    add_nist_qry_smiles()

    add_ion_mode('k0')
    add_ion_mode('k10')
