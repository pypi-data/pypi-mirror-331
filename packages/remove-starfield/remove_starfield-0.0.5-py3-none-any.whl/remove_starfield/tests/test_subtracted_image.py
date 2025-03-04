from copy import deepcopy

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import pytest

import remove_starfield
from .test_core import starfield


@pytest.fixture(scope='session')
def subtracted_image(starfield):
    test_file = remove_starfield.utils.test_data_path(
        'WISPR_files_preprocessed_quarter_size_L3',
        'psp_L3_wispr_20221206T223017_V1_1221.fits')
    
    return starfield.subtract_from_image(test_file)


# pytest-mpl's default style causes wacky artifacts on the blurred input data
@pytest.mark.mpl_image_compare(style="default")
def test_subtracted_image_plot_comparison(subtracted_image):
    subtracted_image.plot_comparison()
    return plt.gcf()


# pytest-mpl's default style causes wacky artifacts on the blurred input data
@pytest.mark.mpl_image_compare(style="default")
def test_subtracted_image_plot_comparison_no_nans(subtracted_image):
    subtracted_image = deepcopy(subtracted_image)
    subtracted_image.source_data = np.nan_to_num(subtracted_image.source_data)
    subtracted_image.blurred_data = np.nan_to_num(subtracted_image.blurred_data)
    subtracted_image.subtracted = np.nan_to_num(subtracted_image.subtracted)
    subtracted_image.plot_comparison()
    return plt.gcf()


# pytest-mpl's default style causes wacky artifacts on the blurred input data
@pytest.mark.mpl_image_compare(style="default")
def test_subtracted_image_plot_comparison_bwr(subtracted_image):
    subtracted_image.plot_comparison(bwr=True, vmin=-3e-12, vmax=3e-12)
    return plt.gcf()


def test_subtracted_image_save(tmp_path, subtracted_image):
    test_path = tmp_path / 'test_image.fits'
    subtracted_image.save(test_path)
    saved = fits.getdata(test_path)
    np.testing.assert_array_equal(saved, subtracted_image.subtracted)
    actual_header = fits.getheader(test_path)
    del actual_header['HISTORY']
    expected_header = fits.Header(subtracted_image.meta)
    del expected_header['HISTORY']
    assert actual_header == expected_header
    
    with pytest.raises(OSError, match='.*already exists.*'):
        subtracted_image.save(test_path)
    subtracted_image.save(test_path, overwrite=True)