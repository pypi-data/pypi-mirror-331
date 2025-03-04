import cv2
from .basic import num_comps

def rgb_to_gray(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2GRAY)

def gray_to_rgb(x):
	assert num_comps(x) == 1
	return cv2.cvtColor(x,cv2.COLOR_GRAY2RGB)