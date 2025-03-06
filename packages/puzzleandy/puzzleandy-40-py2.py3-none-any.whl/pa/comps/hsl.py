from pa.misc.basic import get_comp,set_comp
from pa.space.hsl import rgb_to_hsl,hsl_to_rgb

def get_hsl_comp(im,i):
	im = rgb_to_hsl(im)
	return get_comp(im,i)

def set_hsl_comp(im,i,cp):
	im = rgb_to_hsl(im)
	im = set_comp(im,i,cp)
	return hsl_to_rgb(im)

def get_hsl_h(im):
	return get_hsl_comp(im,0)

def set_hsl_h(im,hp):
	return set_hsl_comp(im,0,hp)

def get_hsl_s(im):
	return get_hsl_comp(im,1)

def set_hsl_s(im,sp):
	return set_hsl_comp(im,1,sp)

def get_hsl_l(im):
	return get_hsl_comp(im,2)

def set_hsl_l(im,sp):
	return set_hsl_comp(im,2,lp)