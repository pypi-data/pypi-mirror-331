def gray_to_bgr(x):
	assert num_comps(x) == 1
	return cv2.cvtColor(x,cv2.COLOR_GRAY2BGR)

def bgr_to_gray(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_BGR2GRAY)

def bgra_to_gray(x):
	assert num_comps(x) == 4
	return cv2.cvtColor(x,cv2.COLOR_BGRA2GRAY)

def gray_to_bgra(x):
	assert num_comps(x) == 1
	return cv2.cvtColor(x,cv2.COLOR_GRAY2BGRA)

def gray_to_rgb(x):
	assert num_comps(x) == 1
	return cv2.cvtColor(x,cv2.COLOR_GRAY2RGB)

def gray_to_rgba(x):
	assert num_comps(x) == 1
	return cv2.cvtColor(x,cv2.COLOR_GRAY2RGBA)

def rgb_to_gray(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGB2GRAY)

def rgba_to_gray(x):
	assert num_comps(x) == 3
	return cv2.cvtColor(x,cv2.COLOR_RGBA2GRAY)