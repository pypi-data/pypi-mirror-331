# get the version
from importlib.metadata import version
__version__ = version('deepGreen')
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from . import utils
from .vsl import VSL

