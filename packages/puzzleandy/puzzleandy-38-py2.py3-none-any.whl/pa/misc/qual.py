import numpy as np
from .math import clamp,min3,max3
from .smoothstep import up_smoothstep as uf
from .smoothstep import down_smoothstep as df

def lin_qual(im,ux,uw,dx,dw):
	if ux <= dx:
		return np.minimum(uf(im,ux,uw),df(im,dx,dw))
	else:
		return np.maximum(uf(im,ux,uw),df(im,dx,dw))

def circ_qual(im,ux,uw,dx,dw):
	if ux <= dx:
		return max3(
			np.minimum(uf(im+360,ux,uw),df(im+360,dx,dw)),
			np.minimum(uf(im,ux,uw),df(im,dx,dw)),
			np.minimum(uf(im-360,ux,uw),df(im-360,dx,dw))
		)
	else:
		return min3(
			np.maximum(uf(im+360,ux,uw),df(im+360,dx,dw)),
			np.maximum(uf(im,ux,uw),df(im,dx,dw)),
			np.maximum(uf(im-360,ux,uw),df(im-360,dx,dw))
		)