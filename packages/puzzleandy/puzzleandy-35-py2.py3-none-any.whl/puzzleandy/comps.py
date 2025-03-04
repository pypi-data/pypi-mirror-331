import cv2
from .basic import get_comp,set_comp
from .hsl import rgb_to_hsl

def get_hue(x):
	x = rbg_to_hsl(x)
	return get_comp(x,0)

def set_hue(x,y):
	x = rgb_to_hsl(x)
	return set_comp(x,0,y)

def get_sat(x):
	x = rbg_to_hsl(x)
	return get_comp(x,1)

def set_sat(x,y):
	x = rgb_to_hsl(x)
	return set_comp(x,1,y)