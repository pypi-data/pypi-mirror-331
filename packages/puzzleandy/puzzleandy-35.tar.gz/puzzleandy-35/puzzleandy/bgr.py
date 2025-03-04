import cv2
from .basic import num_comps

def rgb_to_bgr(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2BGR)

def bgr_to_rgb(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_BGR2RGB)