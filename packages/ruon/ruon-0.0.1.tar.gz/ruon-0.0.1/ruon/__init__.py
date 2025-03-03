from .exception import UnwrapError
from .result import Result, Ok, Err
from .option import Option, Some
from .version import __version__

name = "ruon"

__all__ = ["__version__", "Result", "Ok", "Err", "Option", "Some", "UnwrapError"]
