import cv2
import numpy as np
import PIL
import wand.image
from pa.alpha import rgba_to_bgra,bgra_to_rgba
from .basic import get_num_comps
from pa.space.bgr import rgb_to_bgr,bgr_to_rgb
from .type import to_float,to_uint

def from_cv(im):
	match get_num_comps(im):
		case 3:
			im = bgr_to_rgb(im)
		case 4:
			im = bgra_to_rgba(im)
	return to_float(im)

def to_cv(im):
	match get_num_comps(im):
		case 3:
			im = rgb_to_bgr(im)
		case 4:
			im = rgba_to_bgra(im)
	return to_uint(im)

def from_pil(im):
	im = np.array(im)
	return to_float(im)

def to_pil(im):
	im = to_uint(im)
	return PIL.Image.fromarray(im)

def from_wand(im):
	im = np.array(im)
	return to_float(im)

def to_wand(im):
	im = to_uint(im)
	return wand.image.Image.from_array(im)

def show(im):
	im = to_cv(im)
	cv2.imshow('',im)
	cv2.waitKey()