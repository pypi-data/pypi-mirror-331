from pa.misc.basic import get_comp,set_comp

def get_r(im):
	return get_comp(im,0)

def set_r(im,rp):
	return set_comp(im,0,rp)

def get_g(im):
	return get_comp(im,1)

def set_g(im,gp):
	return set_comp(im,1,gp)

def get_b(im):
	return get_comp(im,2)

def set_b(im,bp):
	return set_comp(im,2,bp)

def get_c(im):
	g = get_g(im)
	b = get_b(im)
	return (g+b)/2

def set_c(im,cp):
	g = get_g(im)
	b = get_b(im)
	c = get_c(im)
	dc = cp-c
	gp = g+dc
	bp = b+dc
	im = set_g(im,gp)
	im = set_b(im,bp)
	return im

def get_m(im):
	r = get_r(im)
	b = get_b(im)
	return (r+b)/2

def set_m(im,mp):
	r = get_r(im)
	b = get_b(im)
	m = get_m(im)
	dm = mp-m
	rp = r+dm
	bp = b+dm
	im = set_r(im,rp)
	im = set_b(im,bp)
	return im

def get_y(im):
	r = get_r(im)
	g = get_g(im)
	return (r+g)/2

def set_y(im,yp):
	r = get_r(im)
	g = get_g(im)
	y = get_y(im)
	dy = yp-y
	rp = r+dy
	gp = g+dy
	im = set_comp(im,0,rp)
	im = set_comp(im,1,gp)
	return im