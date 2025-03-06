from coloraide import Color
import numpy as np
from scipy.interpolate import (
	LinearNDInterpolator,
	PchipInterpolator)
from .util import unlerp

def idx(x,y):
	n = len(x)
	if x[-1] <= y or y <= x[0]:
		return 0;
	else:
		for i in range(n):
			if x[i] > y:
				return i

def lookup(locs,vals,loc_interps,val_interps,loc):
	n = len(locs)
	j = idx(locs,loc)
	i = (j-1)%n
	t = unlerp(loc,locs[i],locs[j])
	t = loc_interps[i](t)
	return val_interps[i](t)

def smoothstep(x):
	return 3*x**2-2*x**3

def make_fmap(
	w,h,
	fac_locs,facs,fac_mids):

	n = len(col_locs)

	fac_loc_interps = [None]*(n-1)
	fac_interps = [None]*(n-1)
	for i in range(n-1):
		xp = [0,fac_mids[i],1]
		fp = [0,0.5,1]
		fac_loc_interps[i] = PchipInterpolator(xp,fp)
		xp = [0,1]
		fp = [facs[i],facs[i+1]]
		fac_interps[i] = lambda x: smoothstep(x)

	img = np.empty((1,w),np.float32)
	for i in range(w):
		loc = mod(360*i/(w-1),360)
		fac = lookup(fac_locs,facs,fac_loc_interps,fac_interps,loc)
		if fac < 0 or fac > 1:
			print(fac)
		img[0,i] = fac
	return np.tile(img,(h,1,1))