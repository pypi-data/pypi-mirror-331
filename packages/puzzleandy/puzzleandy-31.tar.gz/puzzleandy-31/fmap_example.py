from puzzleandy import *

from coloraide import Color
from importlib.resources import files
from math import fmod
import numpy as np
from pathlib import Path
from scipy.interpolate import (
	LinearNDInterpolator,
	PchipInterpolator)
#from .util import unlerp

def idx(x,y):
	n = len(x)
	if x[-1] <= y or y <= x[0]:
		return 0;
	else:
		for i in range(n):
			if x[i] > y:
				return i

def angle_diff(a,b):
	return (a-b)%360

def unlerp_angle(tx,t0,t1):
	d1 = angle_diff(tx,t0)
	d2 = angle_diff(t1,t0)
	return d1/d2

def lookup(locs,vals,loc_interps,val_interps,loc):
	n = len(locs)
	if len(locs) == 1:
		return vals[0]
	else:
		j = idx(locs,loc);
		i = (j-1)%n
		t = unlerp_angle(loc,locs[i],locs[j])
		t = loc_interps[i](t)
		return val_interps[i](t)

def make_fmap(
	w,h,
	fac_locs,facs,fac_mids):

	n = len(fac_locs)

	fac_loc_interps = [None]*n
	fac_interps = [None]*n
	for i in range(n):
		j = (i+1)%n
		xp = [0,fac_mids[i],1]
		fp = [0,0.5,1]
		fac_loc_interps[i] = PchipInterpolator(xp,fp)
		fac_interps[i] = Smoothstep(facs[i],facs[j])

	img = np.empty((1,w),np.float32)
	for i in range(w):
		loc = fmod(360*i/(w-1),360)
		fac = lookup(fac_locs,facs,fac_loc_interps,fac_interps,loc)
		img[0,i] = fac
	return np.tile(img,(h,1))

def apply_fmap(img,fmap):
	h = get_hsv_h(img)
	img_w = img.shape[1]
	img_h = img.shape[0]
	fmap_w = fmap.shape[1]
	fmap_h = fmap.shape[0]
	shaders_path = Path('puzzleandy')/'shaders'
	vert_path = shaders_path/'default.vert'
	frag_path = shaders_path/'apply_fmap.frag'
	ctx = moderngl.create_standalone_context()
	prog = ctx.program(
		contents(vert_path),contents(frag_path))
	prog['iChannel0'] = 0
	tex = ctx.texture(
		(img_w,img_h),1,h.tobytes(),dtype='f4')
	tex.use(0)
	prog['iChannel1'] = 1
	tex = ctx.texture(
		(fmap_w,fmap_h),1,fmap.tobytes(),dtype='f4')
	samp = ctx.sampler(False,texture=tex)
	samp.use(1)
	uni = prog['iChannelResolution']
	uni.value = (
		(img_w,img_h,1),
		(fmap_w,fmap_h,1))
	col = ctx.texture((img_w,img_h),4,dtype='f4')
	fbo = ctx.framebuffer([col])
	fbo.use()
	fbo.clear(0,0,0,0)
	verts = ((-1,-1),(1,-1),(1,1),(-1,1))
	verts = np.array(verts, np.float32)
	vbo = ctx.buffer(verts.tobytes())
	vao = ctx.simple_vertex_array(prog,vbo,'pos')
	vao.render(moderngl.TRIANGLE_FAN)
	img = np.frombuffer(
		fbo.read(components=1,dtype='f4'),dtype=np.float32)
	img = img.reshape((img_h,img_w))
	return img

def load(arr,path):
	return np.load(path)

def save(arr,path):
	np.save(path,arr)

fac_locs = [0,120,240]
facs = [0.25,0,-0.5]
fac_mids = [0.5,0.5,0.5]
fmap = make_fmap(1440,120,fac_locs,facs,fac_mids)


img = pelican()
fac = apply_fmap(img,fmap)
s = get_hsv_s(img)
y = get_yuv_y(img)
show(norm(fac*s*y))
y += fac*s*y
show(y)

img = cow()
fac = apply_fmap(img,fmap)
s = get_hsv_s(img)
show(norm(fac*s))
s += fac*s
img = set_hsv_s(img,s)
show(img)