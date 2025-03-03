import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def calculate_annotation_rate_vs_score(search, min_matched_peak=4, score_range=np.arange(0.60, 0.96, 0.05),
                                       total_unique_queries=5358):
    """
    Calculate annotation rate versus score cutoff for a single search mode.

    Parameters:
    -----------
    search : str
        The search mode ('k0' or 'k10')
    min_matched_peak : int
        Minimum number of matched peaks to consider
    score_range : numpy.ndarray
        Range of score cutoffs to evaluate
    total_unique_queries : int
        Total number of unique query IDs in the dataset (5358)

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing score cutoffs and corresponding annotation rates
    """
    df = pd.read_csv(f'{search}_results_mces.tsv', sep='\t')

    # Filter the dataframe
    df = df[(pd.notnull(df['mces_dist'])) & (df['ion_mode_match'])].reset_index(drop=True)
    df = df[df['matched_peak'] >= min_matched_peak].reset_index(drop=True)

    # Define the match condition
    df['match'] = df['mces_dist'] <= mces_dist_cutoff

    annotation_results = []
    for score_cutoff in score_range:
        df_filtered = df[df['score'] >= score_cutoff]

        # Count unique query IDs that have matches above the score threshold
        if df_filtered.empty:
            annotation_rate = 0
        else:
            # Get unique query IDs that can be annotated
            unique_annotated_queries = df_filtered['qry_db_id'].nunique()
            annotation_rate = unique_annotated_queries / total_unique_queries

        annotation_results.append((score_cutoff, annotation_rate))

    return pd.DataFrame(annotation_results, columns=['score_cutoff', 'annotation_rate'])


def calculate_annotation_rate_vs_score_merged(min_matched_peak=4, score_range=np.arange(0.60, 0.96, 0.05),
                                              total_unique_queries=5358):
    """
    Calculate annotation rate versus score cutoff for merged search modes.

    Parameters:
    -----------
    min_matched_peak : int
        Minimum number of matched peaks to consider
    score_range : numpy.ndarray
        Range of score cutoffs to evaluate
    total_unique_queries : int
        Total number of unique query IDs in the dataset (5358)

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing score cutoffs and corresponding annotation rates
    """
    df1 = pd.read_csv('k0_results_mces.tsv', sep='\t')
    df2 = pd.read_csv('k10_results_mces.tsv', sep='\t')

    df = pd.concat([df1, df2]).reset_index(drop=True)

    # Define the match condition
    df['match'] = df['mces_dist'] <= mces_dist_cutoff

    # Filter the dataframe
    df = df[(pd.notnull(df['mces_dist'])) & (df['ion_mode_match'])].reset_index(drop=True)
    df = df[df['matched_peak'] >= min_matched_peak].reset_index(drop=True)

    # Sort by score
    df = df.sort_values(['qry_db_id', 'score'], ascending=[True, False])

    annotation_results = []
    for score_cutoff in score_range:
        df_filtered = df[df['score'] >= score_cutoff]

        if df_filtered.empty:
            annotation_rate = 0
        else:
            # Get unique query IDs that can be annotated (considering merged results)
            unique_annotated_queries = df_filtered['qry_db_id'].nunique()
            annotation_rate = unique_annotated_queries / total_unique_queries

        annotation_results.append((score_cutoff, annotation_rate))

    return pd.DataFrame(annotation_results, columns=['score_cutoff', 'annotation_rate'])


def gen_all_annotation_rate_results(min_matched_peak=4, total_unique_queries=5358):
    """
    Generate annotation rate results for all search modes and save to a TSV file.

    Parameters:
    -----------
    min_matched_peak : int
        Minimum number of matched peaks to consider
    total_unique_queries : int
        Total number of unique query IDs in the dataset (5358)
    """
    annotation_df_k0 = calculate_annotation_rate_vs_score('k0', min_matched_peak,
                                                          total_unique_queries=total_unique_queries)
    annotation_df_k0['mode'] = 'k0'

    annotation_df_k10 = calculate_annotation_rate_vs_score('k10', min_matched_peak,
                                                           total_unique_queries=total_unique_queries)
    annotation_df_k10['mode'] = 'k10'

    annotation_df = calculate_annotation_rate_vs_score_merged(min_matched_peak,
                                                              total_unique_queries=total_unique_queries)
    annotation_df['mode'] = 'merged'

    # Merge dataframes
    annotation_df = pd.concat([annotation_df_k0, annotation_df_k10, annotation_df]).reset_index(drop=True)

    # annotation_df.to_csv(f'annotation_rate_df_minpeak{min_matched_peak}.tsv', sep='\t', index=False)

    return annotation_df


def plot_annotation_rate(min_matched_peak, total_unique_queries=5358):
    """
    Plot annotation rate versus score cutoff for different search modes.

    Parameters:
    -----------
    min_matched_peak : int
        Minimum number of matched peaks used in the analysis
    total_unique_queries : int
        Total number of unique query IDs in the dataset (5358)
    """
    # Read the data (or generate if not available)
    try:
        df = pd.read_csv(f'annotation_rate_df_minpeak{min_matched_peak}.tsv', sep='\t')
    except FileNotFoundError:
        df = gen_all_annotation_rate_results(min_matched_peak, total_unique_queries)

    # Set the font to Arial
    plt.rcParams['font.family'] = 'Arial'

    # Create the plot
    plt.figure(figsize=(5, 3))

    # Plot lines and scatter points for each mode
    for i, mode in enumerate(df['mode'].unique()):
        mode_data = df[df['mode'] == mode]
        label = ['Non-scaled', 'Scaled', 'Search both'][i]
        plt.plot(mode_data['score_cutoff'], mode_data['annotation_rate'], label=label)
        plt.scatter(mode_data['score_cutoff'], mode_data['annotation_rate'], s=15)

    # Customize the plot
    plt.xlabel('Score cutoff', fontname='Arial', fontsize=14, labelpad=8, color='0.2')
    plt.ylabel('Annotation rate', fontname='Arial', fontsize=14, labelpad=6, color='0.2')
    plt.legend(prop={'family': 'Arial'})
    plt.grid(True, linestyle='--', alpha=0.3)
    # Set y-axis limits to focus on the relevant data range
    # Let's set a more appropriate range instead of the full 0-1 range
    # This will be determined dynamically based on the data
    min_rate = max(0, df['annotation_rate'].min() - 0.05)  # 5% padding below min
    max_rate = min(1.0, df['annotation_rate'].max() + 0.05)  # 5% padding above max
    plt.ylim(min_rate, max_rate)

    plt.title(f'Minimum matched peak: {min_matched_peak}', fontname='Arial', fontsize=14, pad=10, color='0.2')

    # Adjust frame color to 0.4 (gray) and increase tick length
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_edgecolor('0.4')
    ax.tick_params(width=1, length=2, color='0.4')

    # Ensure all text uses Arial
    for text in plt.gca().get_children():
        if isinstance(text, plt.Text):
            text.set_fontname('Arial')

    # Show the plot
    plt.tight_layout()

    # Save as svg
    # plt.savefig(f'annotation_rate_plot_minpeak{min_matched_peak}.svg', transparent=True)
    plt.show()


def plot_fdr_annotation_rate_combined(min_matched_peak, total_unique_queries=5358):
    """
    Create a combined plot showing both FDR and annotation rate curves.

    Parameters:
    -----------
    min_matched_peak : int
        Minimum number of matched peaks used in the analysis
    total_unique_queries : int
        Total number of unique query IDs in the dataset (5358)
    """
    # Read the data
    try:
        fdr_df = pd.read_csv(f'fdr_df_minpeak{min_matched_peak}.tsv', sep='\t')
    except FileNotFoundError:
        print(f"FDR data for min_matched_peak={min_matched_peak} not found. Please run gen_all_results first.")
        return

    try:
        annotation_df = pd.read_csv(f'annotation_rate_df_minpeak{min_matched_peak}.tsv', sep='\t')
    except FileNotFoundError:
        annotation_df = gen_all_annotation_rate_results(min_matched_peak, total_unique_queries)

    # Set the font to Arial
    plt.rcParams['font.family'] = 'Arial'

    # Create the figure with two y-axes
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax2 = ax1.twinx()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, orange, green

    # Plot FDR on the left y-axis
    for i, mode in enumerate(fdr_df['mode'].unique()):
        mode_data = fdr_df[fdr_df['mode'] == mode]
        label = ['Non-scaled', 'Scaled', 'Search both'][i]
        ax1.plot(mode_data['score_cutoff'], mode_data['fdr'], '--', color=colors[i],
                 label=f'{label} (FDR)', alpha=0.7)
        ax1.scatter(mode_data['score_cutoff'], mode_data['fdr'], s=15, color=colors[i], alpha=0.7)

    # Plot annotation rate on the right y-axis
    for i, mode in enumerate(annotation_df['mode'].unique()):
        mode_data = annotation_df[annotation_df['mode'] == mode]
        label = ['Non-scaled', 'Scaled', 'Search both'][i]
        ax2.plot(mode_data['score_cutoff'], mode_data['annotation_rate'], '-', color=colors[i],
                 label=f'{label} (Annotation rate)')
        ax2.scatter(mode_data['score_cutoff'], mode_data['annotation_rate'], s=15, color=colors[i])

    # Customize the plot
    ax1.set_xlabel('Score cutoff', fontname='Arial', fontsize=14, labelpad=8, color='0.2')
    ax1.set_ylabel('FDR', fontname='Arial', fontsize=14, labelpad=6, color='0.2')
    ax2.set_ylabel('Annotation rate', fontname='Arial', fontsize=14, labelpad=6, color='0.2')

    # Add two separate legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', prop={'family': 'Arial'})

    ax1.grid(True, linestyle='--', alpha=0.3)
    ax1.set_ylim(0, 0.6)
    # Set y-axis limits for annotation rate to focus on the relevant data range
    min_rate = max(0, annotation_df['annotation_rate'].min() - 0.05)  # 5% padding below min
    max_rate = min(1.0, annotation_df['annotation_rate'].max() + 0.05)  # 5% padding above max
    ax2.set_ylim(min_rate, max_rate)

    plt.title(f'FDR and Annotation Rate vs Score (Min matched peak: {min_matched_peak})',
              fontname='Arial', fontsize=14, pad=10, color='0.2')

    # Adjust frame color
    for spine in ax1.spines.values():
        spine.set_edgecolor('0.4')
    for spine in ax2.spines.values():
        spine.set_edgecolor('0.4')
    ax1.tick_params(width=1, length=2, color='0.4')
    ax2.tick_params(width=1, length=2, color='0.4')

    # Show the plot
    plt.tight_layout()

    # Save as svg
    # plt.savefig(f'fdr_annotation_rate_combined_minpeak{min_matched_peak}.svg', transparent=True)
    plt.show()


if __name__ == '__main__':
    mces_dist_cutoff = 4
    total_unique_queries = 5358  # Total unique query ID count

    # Generate annotation rate data for different minimum matched peaks
    for min_peak in [3, 4, 5, 6]:
        gen_all_annotation_rate_results(min_matched_peak=min_peak, total_unique_queries=total_unique_queries)

    # Plot annotation rate for different minimum matched peaks
    for min_peak in [3, 4, 5, 6]:
        plot_annotation_rate(min_matched_peak=min_peak, total_unique_queries=total_unique_queries)

    # Optional: Create combined FDR and annotation rate plots
    for min_peak in [3, 4, 5, 6]:
        plot_fdr_annotation_rate_combined(min_matched_peak=min_peak, total_unique_queries=total_unique_queries)