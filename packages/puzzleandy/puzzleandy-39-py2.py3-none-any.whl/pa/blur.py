import cv2
from math import exp
from .comps import num_comps

def box_blur(x,n):
	k = np.ones(n)/n
	return cv2.sepFilter2D(x,-1,k,k)

def ceil_odd(x):
	return 2*floor(x/2)+1

def gauss_blur(x,n=None,s=None):
	if not n:
		if num_comps(x) == 1:
			n = round(6*s+1)
		else:
			n = round(8*s+1)
		n = ceil_odd(n)
	if not s:
		s = 0.15*n+0.35
	k = np.empty(n)
	for i in range(0,n):
		k[i] = exp(-(i-(n-1)/2)**2/(2*s**s))
	k /= np.sum(k)
	return cv2.sepFilter2D(x,-1,k,k)