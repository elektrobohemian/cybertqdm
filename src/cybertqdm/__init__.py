from .cybertqdm import cybertqdm, CyberTqdm
from importlib.metadata import version

__all__ = ["CyberTqdm", "cybertqdm"]
__version__ = version("cybertqdm")
