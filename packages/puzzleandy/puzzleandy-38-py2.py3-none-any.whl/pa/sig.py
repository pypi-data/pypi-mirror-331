import numpy as np
from pa.misc.math import *

def sig(x,k):
	return (x-x*k)/(k-np.abs(x)*2*k+1)