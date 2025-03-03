"""
monarchtominttoreport
"""
from monarchtominttoreport.convert import convert_csv as convert_csv
__version__ = "0.2a1"
__all__ = ["convert", "convert_csv"]

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("monarchtominttoreport")
except PackageNotFoundError:
    # package is not installed
    pass