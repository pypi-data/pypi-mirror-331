import cv2
from pa.misc.basic import get_num_comps

def rgb_to_lab(im):
	assert get_num_comps(im) == 3
	return cv2.cvtColor(im,cv2.COLOR_RGB2LAB)

def lab_to_rgb(im):
	assert get_num_comps(im) == 3
	return cv2.cvtColor(im,cv2.COLOR_LAB2RGB)