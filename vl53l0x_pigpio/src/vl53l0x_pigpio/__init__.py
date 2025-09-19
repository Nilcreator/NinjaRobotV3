#
# (c) 2025 Yoichi Tanibayashi
#
from importlib.metadata import version
from .click_utils import click_common_opts
from .driver import VL53L0X
from .my_logger import get_logger

if __package__:
    __version__ = version(__package__)
else:
    __version__ = "_._._"

    
__all__ = [
    "__version__",
    "click_common_opts",
    "get_logger",
    "VL53L0X"
]
