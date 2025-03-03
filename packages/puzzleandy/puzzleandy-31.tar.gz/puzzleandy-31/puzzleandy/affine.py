import cv2
from .lib_convert import from_wand,to_wand

def flip_hor(x):
	return cv2.flip(x,1)

def flip_vert(x):
	return cv2.flip(x,0)

def rot(x,t):
	x = to_wand(x)
	t = -rad_to_deg(t)
	x.rotate(t)
	return from_wand(x)

def rot_90(x):
	return cv2.rotate(x,cv2.ROTATE_90_COUNTERCLOCKWISE)

def rot_180(x):
	return cv2.rotate(x,cv2.ROTATE_180)

def rot_270(x):
	return cv2.rotate(x,cv2.ROTATE_90_CLOCKWISE)