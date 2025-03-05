from .main import download, imshows
from .house import load_boston
from .img2data import digit_split

__all__ = ["download", 'imshows', 'load_boston', 'digit_split']
__version__ = '0.2.1'