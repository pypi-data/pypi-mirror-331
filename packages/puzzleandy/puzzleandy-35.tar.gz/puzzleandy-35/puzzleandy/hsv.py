import cv2
from .comps import *

def hsv_to_rgb(x):
	return cv2.cvtColor(x,cv2.COLOR_HSV2RGB)

def rgb_to_hsv(x):
	return cv2.cvtColor(x,cv2.COLOR_RGB2HSV)

def get_h(x):
	x = rgb_to_hsv(x)
	return get_comp(x,0)

def get_s(x):
	x = rgb_to_hsv(x)
	return get_comp(x,1)

def get_v(x):
	x = rgb_to_hsv(x)
	return get_comp(x,2)