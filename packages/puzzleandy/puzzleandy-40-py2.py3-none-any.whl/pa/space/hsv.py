import cv2
from pa.misc.basic import get_num_comps

def rgb_to_hsv(im):
	return cv2.cvtColor(im,cv2.COLOR_RGB2HSV)

def hsv_to_rgb(im):
	return cv2.cvtColor(im,cv2.COLOR_HSV2RGB)