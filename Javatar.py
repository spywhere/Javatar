from .commands import *
from .core.event_handler import *
from .utils import (
    Constant
)


def plugin_loaded():
    Constant.startup()
