from importlib.resources import files
import moderngl
import numpy as np
from pa.comps.hsl import (
	get_hsl_h,set_hsl_h,
	get_hsl_s,set_hsl_s)
from pa.space.gray import rgb_to_gray

# normal group

def normal(b,t):
	return t

# darken group

def darken(b,t):
	return np.minimum(b,t)

def multiply(b,t):
	return b*t

def color_burn(b,t):
	invalid = np.geterr()['invalid']
	np.seterr(invalid='ignore')
	r = np.where(
		b == 1,1,np.where(
		t == 0,0,1-np.minimum((1-b)/t,1)))
	np.seterr(invalid=invalid)
	return r

def linear_burn(b,t):
	return np.maximum(b+t-1,0)

def darker_color(b,t):
	bY = rgb_to_gray(b).atleast_3d()
	tY = rgb_to_gray(t).atleast_3d()
	return np.where(bY < tY,b,t)

# lighten group

def lighten(b,t):
	return np.maximum(b,t)

def screen(b,t):
	return b+t-b*t

def color_dodge(b,t):
	invalid = np.geterr()['invalid']
	np.seterr(invalid='ignore')
	r = np.where(
		b == 0,0,np.where(
		t == 1,1,1-np.minimum(b/(1-t),1)))
	np.seterr(invalid=invalid)
	return r

def linear_dodge(b,t):
	return np.minimum(b+t,1)

def lighter_color(b,t):
	bY = rgb_to_gray(b).atleast_3d()
	tY = rgb_to_gray(t).atleast_3d()
	return np.where(bY < tY,t,b)

# contrast group

def overlay(b,t):
	return hard_light(t,b)

def soft_light(b,t):
	return np.where(t <= 0.5,
		2*b*t+(1-2*t)*b**2,
		2*b*(1-t)+(2*t-1)*b**0.5)

def hard_light(b,t):
	return np.where(t <= 0.5,
		multiply(b,2*t),
		screen(b,2*t-1))

def vivid_light(b,t):
	return np.where(t <= 0.5,
		color_burn(b,2*t),
		color_dodge(b,2*t-1))

def linear_light(b,t):
	return np.where(t <= 0.5,
		linear_burn(b,2*t),
		linear_dodge(b,2*t-1))

def pin_light(b,t):
	return np.where(t <= 0.5,
		darken(b,2*t),
		lighten(b,2*t-1))

def hard_mix(b,t):
	return np.floor(b+t)

# inversion group

def difference(b,t):
	return np.maximum(b-t,t-b)

def exclusion(b,t):
	return b+t-2*b*t

# cancellation group

def subtract(b,t):
	return np.maximum(b-t,0)

def divide(b,t):
	invalid = np.geterr()['invalid']
	np.seterr(invalid='ignore')
	r = np.where(
		b == 0,0,np.where(
		b >= t,1,b/t))
	np.seterr(invalid=invalid)
	return r

# component group

def hue(b,t):
	tH = get_hue(t)
	return set_hue(b,tH)

def saturation(b,t):
	tS = get_sat(t)
	return set_sat(b,tS)

#def color(b,t):
	#bL = get_lum(b)
	#return set_lum(t,bL)

#def luminosity(b,t):
	#return color(t,b)