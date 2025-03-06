from pa.misc.basic import get_comp,set_comp
from pa.space.lab import rgb_to_lab,lab_to_rgb

def get_lab_comp(im,i):
	im = rgb_to_lab(im)
	return get_comp(im,i)

def set_lab_comp(im,i,xp):
	im = rgb_to_lab(im)
	im = set_comp(im,i,xp)
	return lab_to_rgb(im)

def get_lab_l(im):
	return get_lab_comp(im,0)

def set_lab_l(im,lp):
	return set_lab_comp(im,0,lp)

def get_lab_a(im):
	return get_lab_comp(im,1)

def set_lab_a(im,ap):
	return set_lab_comp(im,1,ap)

def get_lab_b(im):
	return get_lab_comp(im,1)

def set_lab_b(im,bp):
	return set_lab_comp(im,1,bp)