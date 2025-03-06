from pa.misc.basic import get_comp,set_comp
from pa.space.yuv import rgb_to_yuv,yuv_to_rgb

def get_yuv_comp(im,i):
	im = rgb_to_yuv(im)
	return get_comp(im,i)

def set_yuv_comp(im,i,cp):
	im = rgb_to_yuv(im)
	im = set_comp(im,i,cp)
	return yuv_to_rgb(im)

def get_yuv_y(im):
	return get_yuv_comp(im,0)

def set_yuv_y(im,yp):
	return set_yuv_comp(im,0,yp)

def get_yuv_u(im):
	return get_yuv_comp(im,1)

def set_yuv_u(im,up):
	return set_yuv_comp(im,1,up)

def get_yuv_v(im):
	return get_yuv_comp(im,2)

def set_yuv_v(im,vp):
	return set_yuv_comp(im,2,vp)