import cv2
from pa.misc.basic import get_num_comps

def rgb_to_hsl(im):
	assert get_num_comps(im) == 3
	im = cv2.cvtColor(im,cv2.COLOR_RGB2HLS)
	im[:,:,[1,2]] = im[:,:,[2,1]]
	return im

def hsl_to_rgb(im):
	assert get_num_comps(im) == 3
	im[:,:,[1,2]] = im[:,:,[2,1]]
	return cv2.cvtColor(im,cv2.COLOR_HLS2RGB)