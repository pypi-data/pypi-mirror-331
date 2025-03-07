__author__ = "Johannes Wirth"
__email__ = "j.wirth@tum.de"
__version__ = "0.6.6"

# check if napari is available
try:
    import napari
    WITH_NAPARI = True
except ImportError:
    WITH_NAPARI = False

from insitupy._constants import CACHE

from . import images as im
from . import io
from . import plotting as pl
from . import utils
from ._core.dataclasses import AnnotationsData, BoundariesData, ImageData
from ._core.insitudata import (InSituData, calc_distance_of_cells_from,
                               differential_gene_expression)
from ._core.insituexperiment import InSituExperiment
from ._core.reader import read_xenium
from ._core.registration import register_images
from .palettes import CustomPalettes

__all__ = [
    "InSituData",
    "AnnotationsData",
    "BoundariesData",
    "ImageData",
    "im",
    "utils"
]