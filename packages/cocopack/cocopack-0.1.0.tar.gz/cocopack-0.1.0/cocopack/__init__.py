__version__ = "0.1.0"

from . import notebook

from os import environ

if not environ.get('ZERO_STYLE', False):
    notebook.stylizer.auto_style()

from .shellpack import *

__all__ = ['set_autoreload', 'auto_style']