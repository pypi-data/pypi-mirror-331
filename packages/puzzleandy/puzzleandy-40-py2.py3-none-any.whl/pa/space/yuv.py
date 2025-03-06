import cv2
from pa.misc.basic import get_num_comps

def rgb_to_yuv(x):
	assert get_num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2YUV)

def yuv_to_rgb(x):
	assert get_num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_YUV2RGB)