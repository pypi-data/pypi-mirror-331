try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from ._sample_data import load_conifer_sample_data
from ._widget import label_vectorization_widget

__all__ = (
    "label_vectorization_widget",
    "load_conifer_sample_data",
)
