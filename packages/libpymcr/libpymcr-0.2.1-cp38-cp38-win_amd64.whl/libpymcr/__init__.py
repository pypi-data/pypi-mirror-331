from . import _version
__version__ = _version.get_versions()['version']

from .Matlab import Matlab
from .MatlabProxyObject import MatlabProxyObject
from . import utils

_globalFunctionDict = {}
