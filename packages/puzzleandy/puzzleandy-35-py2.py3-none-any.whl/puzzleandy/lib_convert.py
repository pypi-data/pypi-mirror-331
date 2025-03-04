import cv2
import numpy as np
import PIL
import wand.image
from .alpha import rgba_to_bgra,bgra_to_rgba
from .basic import num_comps
from .bgr import rgb_to_bgr,bgr_to_rgb
from .dtype import to_float,to_uint

def from_cv(x):
	match num_comps(x):
		case 3:
			x = bgr_to_rgb(x)
		case 4:
			x = bgra_to_rgba(x)
	return to_float(x)

def to_cv(x):
	match num_comps(x):
		case 3:
			x = rgb_to_bgr(x)
		case 4:
			x = rgba_to_bgra(x)
	return to_uint(x)

def show(x):
	x = to_cv(x)
	cv2.imshow('',x)
	cv2.waitKey()

def from_pil(x):
	x = np.array(x)
	return to_float(x)

def to_pil(x):
	x = to_uint(x)
	return PIL.Image.fromarray(x)

def from_wand(x):
	x = np.array(x)
	return to_float(x)

def to_wand(x):
	x = to_uint(x)
	return wand.image.Image.from_array(x)