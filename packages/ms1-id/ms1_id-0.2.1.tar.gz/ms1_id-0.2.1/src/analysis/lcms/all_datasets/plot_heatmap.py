import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import rcParams

# Set font to Helvetica for all elements
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Helvetica']
rcParams['xtick.labelsize'] = 3.8
rcParams['ytick.labelsize'] = 4

# Load the data
df = pd.read_csv('lcms_datasets_annotations.tsv', sep='\t', index_col=0)

# Drop the 'Total' column as we don't need it for the heatmap
if 'Total' in df.columns:
    df = df.drop(columns=['Total'])

# Define the custom row order (these are the indices in your data)
row_order = [
    'MSV000095868', 'MSV000090053', 'MSV000085024', 'MSV000090030',
    'MSV000090000', 'MSV000094338', 'MSV000083888', 'MSV000083632',
    'MSV000090975', 'MSV000090968'
]

# Reorder the rows of the dataframe
# First ensure all requested rows exist
available_rows = [row for row in row_order if row in df.index]
# Then reorder
df = df.loc[available_rows]

# Create the white -> blue -> red colormap as in the example
colors = [(1, 1, 1), (0.78, 0.84, 0.94), (0.92, 0.69, 0.65)]  # White -> Blue -> Red
n_bins = 100  # Discretizes the interpolation into bins
cmap_name = 'white_blue_red'
cmap_wbr = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

# Apply log transformation to the data (adding 1 to avoid log(0))
log_df = np.log2(df + 1)

# Create the figure for the heatmap
plt.figure(figsize=(3.4, 1.5))

# Create the heatmap with log-transformed data for colors, but original data for annotations
ax = sns.heatmap(
    log_df,  # Log-transformed data for the colors
    cmap=cmap_wbr,
    linewidths=0.55,
    linecolor='white',
    cbar=False,  # No colorbar in the main plot
    annot=df.astype(int),  # Original data as integers for annotations
    fmt="d",  # Format as integers
    annot_kws={"size": 3.5}  # Smaller font size for annotations
)

# Move x-axis labels to the top
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

# Configure ticks appearance
ax.tick_params(axis='x', length=1, width=0.5, colors='0.2', pad=1)
ax.tick_params(axis='y', length=1.5, width=0.5, colors='0.2', pad=1.5)

# Handle label rotation
plt.xticks(rotation=18, ha='center')

# Get the current y-tick labels
labels = [item.get_text() for item in ax.get_xticklabels()]

# Format the specific long labels into two lines
new_labels = []
for label in labels:
    if label == 'Shikimates and Phenylpropanoids':
        new_labels.append('Shikimates and\nPhenylpropanoids')
    elif label == 'Amino acids and Peptides':
        new_labels.append('Amino acids and\nPeptides')
    else:
        new_labels.append(label)

# Apply the new formatted labels
ax.set_xticklabels(new_labels)

# Set tick labels font
for tick in ax.get_xticklabels():
    tick.set_fontname('Helvetica')
for tick in ax.get_yticklabels():
    tick.set_fontname('Helvetica')

# Add black lines for visual separation if needed
plt.axhline(y=0, color='0.4', linewidth=0.5)
plt.axvline(x=0, color='0.4', linewidth=0.5)

# Tight layout to ensure everything fits
plt.tight_layout()

# Save the main heatmap figure
plt.savefig('np_pathway_heatmap.svg', bbox_inches='tight', transparent=True)


# Create and save a separate colorbar
plt.figure(figsize=(0.75, 0.15))
cbar_ax = plt.axes([0.1, 0.5, 0.8, 0.2])
norm = plt.Normalize(vmin=log_df.min().min(), vmax=log_df.max().max())
sm = plt.cm.ScalarMappable(cmap=cmap_wbr, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, cax=cbar_ax, orientation='horizontal')

# Improve colorbar style
# cbar.set_label('log2(count + 1)', fontsize=3.5, fontname='Helvetica', color='0.2')
cbar.ax.tick_params(
    length=1,          # Shorter tick length
    width=0.5,           # Thinner tick width
    colors='0.4',        # Gray color for ticks
    labelsize=3,       # Match font size with main plot
    pad=0.15               # Padding between ticks and labels
)

# Set tick labels font for colorbar
for tick in cbar.ax.get_xticklabels():
    tick.set_fontname('Helvetica')

# Adjust colorbar frame
cbar.outline.set_linewidth(0)  # Thinner outline
cbar.outline.set_edgecolor('0.4')  # Gray outline

# Save the separate colorbar figure
plt.savefig('colorbar_only.svg', bbox_inches='tight', transparent=True)


plt.show()