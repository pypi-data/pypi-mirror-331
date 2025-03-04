import cv2
from .comps import num_comps

# bgr
# bgra
# gray
# rgb
# rgba

def bgr_to_bgra(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_BGR2BGRA)

def bgr_to_rgb(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2BGR)

def bgr_to_rgba(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_BGR2RGBA)

def bgra_to_bgr(x):
	assert num_comps(x) == 4
	return cv2.cvtColor(x,cv2.COLOR_BGRA2BGR)

def bgra_to_rgb(x):
	assert num_comps(x) == 4
	return cv2.cvtColor(x,cv2.COLOR_BGRA2RGB)

def bgra_to_rgba(x):
	assert num_comps(x) == 4
	return cv2.cvtColor(x,cv2.COLOR_BGRA2RGBA)

def rgb_to_bgr(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2BGR)

def rgb_to_bgra(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2BGRA)

def rgb_to_rgba(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2RGBA)

def rgba_to_bgr(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGBA2BGR)

def rgba_to_bgra(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGBA2BGRA)

def rgba_to_rgb(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGBA2RGB)