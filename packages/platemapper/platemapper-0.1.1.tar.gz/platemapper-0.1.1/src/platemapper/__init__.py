try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from platemapper.platemapper import PlateMapper

__all__ = ["PlateMapper"]
