import ctypes
import platform
from .affine import *
from .apply_cmap import *
from .apply_lut import *
from .basic import *
from .bgr import *
from .blend import *
from .circular_qualifier import *
from .cmaps import *
from .color_mixer import *
from .compand import *
from .comps import *
from .contrast import *
from .delta_e_1976 import *
from .delta_e_1994 import *
from .delta_e_2000 import *
from .dtype import *
from .file_io import *
from .filters import *
from .gray import *
from .hist import *
from .hsl import *
from .hsv import *
from .hue_sat_factor import *
from .interp import *
from .lerp import *
from .lib_convert import *
from .linear_qualifier import *
from .make_cmap import *
from .neutral_lut import *
from .photos import *
from .sd_box import *
from .sig import *
from .tex import *
from .util import *

if platform.system() == 'Windows':
	ctypes.windll.shcore.SetProcessDpiAwareness(1)