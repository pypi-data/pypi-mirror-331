import numpy as np
import pyimzml.ImzMLParser as imzml
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
import matplotlib.colors as colors
from scipy.stats import pearsonr


def get_ion_image_from_imzml(imzml_file, target_mz, tolerance=0.01, intensity_threshold=0):
    parser = imzml.ImzMLParser(imzml_file)

    # Get the maximum x and y coordinates from all spectra
    max_x = max(x for x, y, z in parser.coordinates)
    max_y = max(y for x, y, z in parser.coordinates)

    # Initialize the image array with the maximum dimensions
    image = np.zeros((max_y + 1, max_x + 1))

    for idx, (x, y, z) in enumerate(parser.coordinates):
        mzs, ints = parser.getspectrum(idx)
        mask = np.abs(mzs - target_mz) <= tolerance
        matched_intensities = ints[mask]

        if len(matched_intensities) > 0:
            intensity = np.max(matched_intensities)
            if intensity > intensity_threshold:
                image[y, x] = intensity

    return image, parser.coordinates


def plot_ion_image(image, title=None, colormap='viridis',
                   x_range=None, y_range=None,
                   hot_spot_removal=True, hot_spot_percentile=99.9,
                   apply_median_filter=False,
                   save=False, name='ion_image.svg'):
    """
    Plot the ion image, with options to plot partial data.

    Parameters:
    - image: 2D numpy array representing the ion image
    - title: Optional title for the plot
    - colormap: Colormap to use for the image (default: 'viridis')
    - x_range: Tuple of (start, end) for x-axis. If None, plot all. (default: None)
    - y_range: Tuple of (start, end) for y-axis. If None, plot all. (default: None)
    """
    # Apply ranges if specified
    if x_range is not None:
        image = image[:, x_range[0]:x_range[1]]
    if y_range is not None:
        image = image[y_range[0]:y_range[1], :]

    # Apply processing
    if hot_spot_removal:
        percentile_top = np.percentile(image[image > 0], hot_spot_percentile)
        image[image > percentile_top] = percentile_top

    if apply_median_filter:
        image = median_filter(image, size=3)

    plt.figure(figsize=(10, 8))

    # Create a custom colormap using the later 90% of viridis
    original_cmap = plt.get_cmap(colormap)
    colors_array = original_cmap(np.linspace(0.10, 1, 256))
    custom_cmap = colors.LinearSegmentedColormap.from_list("custom_" + colormap, colors_array)

    plt.imshow(image, cmap=custom_cmap, vmin=0, vmax=np.max(image))
    plt.colorbar(label='Intensity')

    if title:
        plt.title(title)

    plt.axis('off')
    plt.tight_layout()

    if save:
        plt.savefig(name, transparent=True)
    plt.show()


def calculate_ion_image_correlation(image1, image2):
    """
    Calculate the intensity correlation between two ion images,
    considering only pixels where both images have intensities > 0.

    Parameters:
    - image1: 2D numpy array representing the first ion image
    - image2: 2D numpy array representing the second ion image

    Returns:
    - correlation_coefficient: Pearson correlation coefficient
    - p_value: Two-tailed p-value
    """
    # Ensure the images have the same shape
    if image1.shape != image2.shape:
        raise ValueError("The two images must have the same shape")

    # Flatten the 2D images into 1D arrays
    flat_image1 = image1.flatten()
    flat_image2 = image2.flatten()

    # Create a mask for pixels where both images have intensity > 0
    mask = (flat_image1 > 0) & (flat_image2 > 0)

    # Apply the mask to both flattened images
    valid_intensities1 = flat_image1[mask]
    valid_intensities2 = flat_image2[mask]

    # Check if there are enough valid pixels for correlation
    if len(valid_intensities1) < 2:
        return None, None  # Not enough data points for correlation

    # Calculate Pearson correlation
    correlation_coefficient, p_value = pearsonr(valid_intensities1, valid_intensities2)

    return correlation_coefficient, p_value


if __name__ == "__main__":

    ##########################################
    print('='*50)
    # guanosine
    imzml_file = "/Users/shipei/Documents/projects/ms1_id/imaging/spotted_stds/2020-12-05_ME_X190_L1_Spotted_20umss_375x450_33at_DAN_Neg.imzML"

    t_mz = 505.988534
    ion_image_1, _ = get_ion_image_from_imzml(imzml_file, t_mz, tolerance=t_mz*10e-6)
    colormap = 'viridis'  # viridis, cividis, magma, inferno, plasma
    # Plot partial image
    plot_ion_image(ion_image_1,
                   title=None, colormap=colormap,
                   x_range=(None, None), y_range=(None, None),
                   hot_spot_percentile=85,
                   apply_median_filter=False,
                   save=False,
                   name='505.svg')

    t_mz = 487.977964
    ion_image_1, _ = get_ion_image_from_imzml(imzml_file, t_mz, tolerance=t_mz*10e-6)
    colormap = 'viridis'  # viridis, cividis, magma, inferno, plasma
    # Plot partial image
    plot_ion_image(ion_image_1,
                   title=None, colormap=colormap,
                   x_range=(None, None), y_range=(None, None),
                   hot_spot_percentile=85,
                   apply_median_filter=False,
                   save=False,
                   name='487.svg')

    t_mz = 426.022194
    ion_image_1, _ = get_ion_image_from_imzml(imzml_file, t_mz, tolerance=t_mz*10e-6)
    colormap = 'viridis'  # viridis, cividis, magma, inferno, plasma
    # Plot partial image
    plot_ion_image(ion_image_1,
                   title=None, colormap=colormap,
                   x_range=(None, None), y_range=(None, None),
                   hot_spot_percentile=85,
                   apply_median_filter=False,
                   save=False,
                   name='426.svg')

    t_mz = 408.011624
    ion_image_1, _ = get_ion_image_from_imzml(imzml_file, t_mz, tolerance=t_mz*10e-6)
    colormap = 'viridis'  # viridis, cividis, magma, inferno, plasma
    # Plot partial image
    plot_ion_image(ion_image_1,
                   title=None, colormap=colormap,
                   x_range=(None, None), y_range=(None, None),
                   hot_spot_percentile=85,
                   apply_median_filter=False,
                   save=False,
                   name='408.svg')

    #
    # #
    # t_mz = 160.0064
    # ion_image_1, _ = get_ion_image_from_imzml(imzml_file, t_mz, tolerance=t_mz*5e-6)
    # colormap = 'viridis'  # viridis, cividis, magma, inferno, plasma
    # # Plot partial image
    # plot_ion_image(ion_image_1,
    #                title=None, colormap=colormap,
    #                x_range=(None, None), y_range=(None, None),
    #                hot_spot_percentile=99,
    #                apply_median_filter=False,
    #                save=False,
    #                name='ion_image.svg')
    #
    # t_mz = 143.0452
    # ion_image_1, _ = get_ion_image_from_imzml(imzml_file, t_mz, tolerance=t_mz*5e-6)
    # colormap = 'viridis'  # viridis, cividis, magma, inferno, plasma
    # # Plot partial image
    # plot_ion_image(ion_image_1,
    #                title=None, colormap=colormap,
    #                x_range=(None, None), y_range=(None, None),
    #                hot_spot_percentile=99,
    #                apply_median_filter=False,
    #                save=False,
    #                name='ion_image.svg')
    #
    # t_mz = 128.0341
    # ion_image_1, _ = get_ion_image_from_imzml(imzml_file, t_mz, tolerance=t_mz*5e-6)
    # colormap = 'viridis'  # viridis, cividis, magma, inferno, plasma
    # # Plot partial image
    # plot_ion_image(ion_image_1,
    #                title=None, colormap=colormap,
    #                x_range=(None, None), y_range=(None, None),
    #                hot_spot_percentile=99,
    #                apply_median_filter=False,
    #                save=False,
    #                name='ion_image.svg')



