import pandas as pd



def main_fdr(search, score_cutoff=0.8, min_matched_peak=4, mces_dist_cutoff=2):
    df = pd.read_csv(f'{search}_results_mces.tsv', sep='\t')

    df = df[(pd.notnull(df['mces_dist'])) & (df['ion_mode_match'])].reset_index(drop=True)
    df['match'] = df['mces_dist'] <= mces_dist_cutoff


    df = df[(df['score'] >= score_cutoff) & (df['matched_peak'] >= min_matched_peak)].reset_index(drop=True)

    print('====================')
    print(df['match'].value_counts())
    print('FDR: ', sum(df['match'] == False) / df.shape[0])

    # for each qry_id, retain the best match
    df = df.sort_values('score', ascending=False).drop_duplicates('qry_db_id').reset_index(drop=True)
    print('====================')
    print('After best match selection:')
    print(df['match'].value_counts())
    print('FDR: ', sum(df['match'] == False) / df.shape[0])


def search_merged_fdr(score_cutoff=0.8, min_matched_peak=4, mces_dist_cutoff=2):
    mode = 'k10'
    df1 = pd.read_csv('k0_results_mces.tsv', sep='\t')
    df2 = pd.read_csv(f'{mode}_results_mces.tsv', sep='\t')

    df = pd.concat([df1, df2]).reset_index(drop=True)
    df = df[(pd.notnull(df['mces_dist'])) & (df['ion_mode_match'])].reset_index(drop=True)

    df = df[(df['score'] >= score_cutoff) & (df['matched_peak'] >= min_matched_peak)].reset_index(drop=True)
    df.drop_duplicates(subset=['qry_db_id', 'matched_db_id'], inplace=True)

    df['match'] = df['mces_dist'] <= mces_dist_cutoff

    print('====================')
    print(df['match'].value_counts())

    print('FDR: ', sum(df['match'] == False) / df.shape[0])

    # for each qry_id, retain the best match
    df = df.sort_values('score', ascending=False).drop_duplicates('qry_db_id').reset_index(drop=True)
    print('====================')
    print('After best match selection:')
    print(df['match'].value_counts())
    print('FDR: ', sum(df['match'] == False) / df.shape[0])


if __name__ == '__main__':

    mces_dist_cutoff = 4

    min_score = 0.7
    min_peaks = 3
    main_fdr('k0', min_score, min_peaks, mces_dist_cutoff)

    main_fdr('k10', min_score, min_peaks, mces_dist_cutoff)

    search_merged_fdr(min_score, min_peaks, mces_dist_cutoff)
