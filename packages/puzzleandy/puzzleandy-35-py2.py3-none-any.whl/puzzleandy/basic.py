import cv2
import numpy as np

def num_comps(x):
	assert len(x.shape) in [2,3]
	match len(x.shape):
		case 2:
			return 1
		case 3:
			return x.shape[2]

def get_comp(x,i):
	assert i < num_comps(x)
	return cv2.split(x)[i].copy()

def set_comp(x,i,y):
	assert i < num_comps(x)
	x = cv2.split(x)
	return cv2.merge((*x[:i],y,*x[i+1:]))

def solid_color(w,h,c):
	c = np.array(c,np.float32)
	return np.full((h,w,len(c)),c,np.float32)