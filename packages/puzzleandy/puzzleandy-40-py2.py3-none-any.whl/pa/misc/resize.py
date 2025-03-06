import cv2

def resize_to(im1,im2,interp=None):
	return cv2.resize(im1,im2.shape[1::-1],0,0,interp)