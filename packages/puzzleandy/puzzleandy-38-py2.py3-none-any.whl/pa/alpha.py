import cv2
from .misc.basic import get_num_comps

def rgba_to_bgra(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGBA2BGRA)

def bgra_to_rgba(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_BGRA2RGBA)