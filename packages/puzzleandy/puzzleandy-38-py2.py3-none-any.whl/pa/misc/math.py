import cv2
from math import tan
import numpy as np
from .lerp import *

def clamp(im,m=0,M=1):
	return np.clip(im,m,M)

def invert(im):
	return 1-im

def min3(im1,im2,im3):
	return np.minimum(np.minimum(im1,im2),im3)

def max3(im1,im2,im3):
	return np.maximum(np.maximum(im1,im2),im3)

def norm(im,m=0,M=1):
	t = unlerp(x,np.min(x),np.max(x))
	return lerp(t,m,M)

def pt_angle(x,px,py,t):
	return (x-px)*tan(t)+py

def remap(x,m1,M1,m2,M2):
	return lerp(unlerp(x,m1,M1),m2,M2)