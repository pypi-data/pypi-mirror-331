import ctypes
import platform
from .apply_cmap import *
from .apply_lut import *
from .assets.photos import *
from .assets.tex import *
from .circular_qualifier import *
from .cmaps import *
from .color_mixer import *
from .compand import *
from .comps.basic import *
from .comps.hsl import *
from .comps.hsv import *
from .comps.yuv import *
from .contrast import *
from .delta_e_1976 import *
from .delta_e_1994 import *
from .delta_e_2000 import *
from .io import *
from .filters import *
from .hist import *
from .hue_sat_factor import *
from .interp import *
from .linear_qualifier import *
from .make_cmap import *
from .neutral_lut import *
from .misc.affine import *
from .misc.basic import *
from .misc.blend import *
from .misc.lerp import *
from .misc.lib import *
from .misc.math import *
from .misc.qual import *
from .misc.resize import *
from .misc.type import *
from .sd_box import *
from .sig import *
from .space.bgr import *
from .space.gray import *
from .space.hsl import *
from .space.hsv import *
from .space.yuv import *

if platform.system() == 'Windows':
	ctypes.windll.shcore.SetProcessDpiAwareness(1)