from pa.misc.lerp import lerp,unlerp
from pa.misc.math import clamp,remap

class Lerp:

	def __init__(self,f0,f1):
		self.f0 = f0
		self.f1 = f1

	def __call__(self,x):
		return lerp(x,self.f0,self.f1)

class Smoothstep:

	def __init__(self,f0,f1):
		print('init=',f0,f1)
		self.f0 = f0
		self.f1 = f1

	def __call__(self,x):
		f0 = self.f0
		f1 = self.f1
		y = 3*x**2-2*x**3
		return remap(y,0,1,f0,f1)