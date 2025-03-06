import cv2
from pa.misc.basic import get_num_comps

def rgb_to_gray(im):
	assert get_num_comps(im) == 3
	return cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)

def gray_to_rgb(im):
	assert get_num_comps(im) == 1
	return cv2.cvtColor(im,cv2.COLOR_GRAY2RGB)