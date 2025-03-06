import numpy as np
from .lerp import unlerp
from .math import clamp

def smoothstep(x,e1,e2):
	x = clamp(unlerp(x,e1,e2))
	return 3*x**2-2*x**3

def up_smoothstep(x,ux,uw):
	if uw == 0:
		return np.where(x >= ux,1,0).astype(np.float32)
	else:
		return smoothstep(x,ux-uw/2,ux+uw/2)

def down_smoothstep(x,dx,dw):
	if dw == 0:
		return np.where(x <= dx,1,0).astype(np.float32)
	else:
		return smoothstep(x,dx+dw/2,dx-dw/2)