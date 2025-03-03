import cv2
from .space_convert import (
	rgb_to_hsl,hsl_to_rgb,
	rgb_to_hsv,hsv_to_rgb,
	rgb_to_lab,lab_to_rgb,
	rgb_to_yuv,
	rgba_to_yuv)

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
	print('set ',i)
	assert i < num_comps(x)
	x = cv2.split(x)
	return cv2.merge((*x[:i],y,*x[i+1:]))

def get_yuv_y(x):
	assert(num_comps(x) in [3,4])
	match num_comps(x):
		case 3:
			x = rgb_to_yuv(x)
		case 4:
			x = rgba_to_yuv(x)
	return get_comp(x,0)

def get_lab_l(x):
	assert(num_comps(x) in [3,4])
	match num_comps(x):
		case 3:
			x = rgb_to_lab(x)
		case 4:
			x = rgba_to_lab(x)
	return get_comp(x,0)

def set_lab_l(x,l):
	match num_comps(x):
		case 3:
			x = rgb_to_lab(x)
			x = set_comp(x,0,l)
			return lab_to_rgb(x)
		case 4:
			r,g,b,a = cv2.split(x)
			y = cv2.merge((r,g,b))
			y = rgb_to_lab(y)
			y = set_comp(y,0,l)
			y = lab_to_rgb(y)
			r,g,b = cv2.split(y)
			return cv2.merge((r,g,b,a))

def get_hsl_h(x):
	assert(num_comps(x) in [3,4])
	match num_comps(x):
		case 3:
			x = rgb_to_hsl(x)
		case 4:
			x = rgba_to_hsl(x)
	return get_comp(x,0)

def set_hsl_h(x,h):
	match num_comps(x):
		case 3:
			x = rgb_to_hsl(x)
			x = set_comp(x,0,h)
			return hsl_to_rgb(x)
		case 4:
			r,g,b,a = cv2.split(x)
			x = cv2.merge((r,g,b))
			x = rgb_to_hsl(x)
			x = set_comp(x,0,h)
			x = hsl_to_rgb(x)
			r,g,b = cv2.split(x)
			return cv2.merge((r,g,b,a))

def get_hsl_s(x):
	assert(num_comps(x) in [3,4])
	match num_comps(x):
		case 3:
			x = rgb_to_hsl(x)
		case 4:
			x = rgba_to_hsl(x)
	return get_comp(x,2)

def set_hsl_s(x,s):
	match num_comps(x):
		case 3:
			print('RGB')
			x = rgb_to_hsl(x)
			x = set_comp(x,2,s)
			return hsl_to_rgb(x)
		case 4:
			r,g,b,a = cv2.split(x)
			x = cv2.merge((r,g,b))
			x = rgb_to_hsl(x)
			x = set_comp(x,2,s)
			x = hsl_to_rgb(x)
			r,g,b = cv2.split(x)
			return cv2.merge((r,g,b,a))

def get_hsl_l(x):
	x = rgb_to_hsl(x)
	_,l,_ = cv2.split(x)
	return l

def set_hsl_l(x,L):
	x = rgb_to_hsl(x)
	H,_,S = cv2.split(x)
	x = cv2.merge((H,L,S))
	return hsl_to_rgb(x)

def get_hsv_h(x):
	x = rgb_to_hsv(x)
	h,_,_ = cv2.split(x)
	return h

def set_hsv_h(x,h):
	x = rgb_to_hsv(x)
	_,v,s = cv2.split(x)
	x = cv2.merge((h,v,s))
	return hsv_to_rgb(x)

def get_hsv_s(x):
	x = rgb_to_hsv(x)
	_,s,_ = cv2.split(x)
	return s

def set_hsv_s(x,s):
	match num_comps(x):
		case 3:
			print('RGB')
			x = rgb_to_hsv(x)
			x = set_comp(x,1,s)
			return hsv_to_rgb(x)
		case 4:
			r,g,b,a = cv2.split(x)
			x = cv2.merge((r,g,b))
			x = rgb_to_hsv(x)
			x = set_comp(x,1,s)
			x = hsv_to_rgb(x)
			r,g,b = cv2.split(x)
			return cv2.merge((r,g,b,a))

def get_hsv_v(x):
	x = rgb_to_hsv(x)
	_,_,v = cv2.split(x)
	return v

def set_hsv_v(x,v):
	x = rgb_to_hsv(x)
	h,s,_ = cv2.split(x)
	x = cv2.merge((h,s,v))
	return hsv_to_rgb(x)