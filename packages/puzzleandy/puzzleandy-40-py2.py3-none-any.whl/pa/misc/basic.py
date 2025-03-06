import cv2
import numpy as np

def get_num_comps(im):
	assert len(im.shape) in [2,3]
	match len(im.shape):
		case 2:
			return 1
		case 3:
			return im.shape[2]

def set_num_comps(im,n):
	match n:
		case 1:
			return to_gray(im)
		case 3:
			return to_rgb(im)
		case 4:
			return to_rgba(im)

def get_comp(im,i):
	assert i < get_num_comps(im)
	return cv2.split(im)[i].copy()

def set_comp(im,i,xp):
	assert i < get_num_comps(im)
	im = cv2.split(im)
	return cv2.merge((*im[:i],xp,*im[i+1:]))

def solid_color(w,h,c):
	c = np.array(c,np.float32)
	return np.full((h,w,len(c)),c,np.float32)