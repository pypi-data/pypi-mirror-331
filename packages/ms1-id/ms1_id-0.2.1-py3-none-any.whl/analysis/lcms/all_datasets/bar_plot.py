import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set font to Helvetica for all elements
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Helvetica']
rcParams['xtick.labelsize'] = 3.5

# Load the data
df = pd.read_csv('lcms_datasets_annotations.tsv', sep='\t', index_col=0)

# Define the custom row order (in reverse to get correct top-to-bottom order)
row_order = [
    'MSV000095868', 'MSV000090053', 'MSV000085024', 'MSV000090030',
    'MSV000090000', 'MSV000094338', 'MSV000083888', 'MSV000083632',
    'MSV000090975', 'MSV000090968'
]

# Reorder the rows of the dataframe
available_rows = [row for row in row_order if row in df.index]
df = df.loc[available_rows[::-1]]  # Reverse the order for plotting

# Calculate row totals
if 'Total' in df.columns:
    row_totals = df['Total']
else:
    row_totals = df.sum(axis=1)

# Create the figure for the bar plot
fig, ax = plt.figure(figsize=(1, 1.46)), plt.gca()

# Create horizontal bar plot with log scale
bars = ax.barh(row_totals.index, row_totals.values, height=0.7, color='#476f95', alpha=1)
ax.set_xscale('log')  # Use log scale for x-axis

# Add value labels to the end of each bar
for i, bar in enumerate(bars):
    value = row_totals.iloc[i]
    ax.text(
        bar.get_width() * 1.05,  # Slightly to the right of the bar
        bar.get_y() + bar.get_height()/2,  # Vertically centered
        f'{int(value)}',  # Original value as integer
        va='center',
        fontsize=3.5,
        color='black'
    )

# Set the labels
ax.set_xlabel('Total annotations', fontsize=4.25, labelpad=1.5, color='0.2')

# Customize the grid
ax.grid(axis='x', linestyle='--', alpha=0.7, zorder=0, color='0.5', linewidth=0.5)
ax.set_axisbelow(True)  # Put the grid behind the bars

# Remove the y axis
ax.yaxis.set_visible(False)

# Remove the spines
# ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)  # Hide left spine since y-axis is hidden
ax.spines['bottom'].set_visible(False)  # Hide bottom spine as we'll move x-axis to top

# Move x-axis to the top
ax.xaxis.set_ticks_position('top')
ax.xaxis.set_label_position('top')

# Set the color of the frame (axes spines)
for spine in ax.spines.values():
    spine.set_edgecolor('0.4')
    spine.set_linewidth(0.5)

# Adjust x-axis tick length and color
ax.tick_params(
    axis='x',
    which='both',  # Apply to both major and minor ticks
    length=1.5,    # Shorter tick length
    width=0.5,     # Thinner tick width
    colors='0.4',  # Gray color for ticks
    direction='out',
    pad=1.5        # Padding between ticks and labels
)

# Format the x-axis tick labels to show original values, not log values
from matplotlib.ticker import ScalarFormatter
formatter = ScalarFormatter()
formatter.set_scientific(False)
ax.xaxis.set_major_formatter(formatter)

# Tight layout to ensure everything fits
plt.tight_layout()

# Save the figure
plt.savefig('annotations_by_dataset.svg', bbox_inches='tight', transparent=True)

plt.show()