import cv2
from .basic import num_comps

def rgb_to_hsl(x):
	assert num_comps(x) == 3
	x = cv2.cvtColor(x,cv2.COLOR_RGB2HLS)
	x[:,:,[1,2]] = x[:,:,[2,1]]
	return x

def hsl_to_rgb(x):
	assert num_comps(x) == 3
	x[:,:,[1,2]] = x[:,:,[2,1]]
	return cv2.cvtColor(x,cv2.COLOR_HLS2RGB)