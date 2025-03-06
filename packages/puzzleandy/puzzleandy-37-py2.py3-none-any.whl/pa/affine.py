import cv2
from .lib import from_wand,to_wand

def flip_hor(im):
	return cv2.flip(im,1)

def flip_vert(im):
	return cv2.flip(im,0)

def rot(im,t):
	im = to_wand(im)
	t = -rad_to_deg(t)
	im.rotate(t)
	return from_wand(im)

def rot_90(im):
	return cv2.rotate(im,cv2.ROTATE_90_COUNTERCLOCKWISE)

def rot_180(im):
	return cv2.rotate(im,cv2.ROTATE_180)

def rot_270(im):
	return cv2.rotate(im,cv2.ROTATE_90_CLOCKWISE)