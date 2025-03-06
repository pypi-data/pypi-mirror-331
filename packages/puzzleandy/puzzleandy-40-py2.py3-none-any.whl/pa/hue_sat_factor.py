from importlib.resources import files
import moderngl
import numpy as np
from pa.misc.basic import *
from .comps.hsv import rgb_to_hsv
from .comps.lab import rgb_to_lab

from math import *

def hue_sat_factor(img,
	factor_r,factor_y,factor_c,
	factor_g,factor_b,factor_m):
	hsv = rgb_to_hsv(img)
	lab = rgb_to_lab(img)
	lab = lab/100
	w = img.shape[1]
	h = img.shape[0]
	shaders_path = files()/'shaders'
	vert_path = shaders_path/'default.vert'
	frag_path = shaders_path/'hue_sat_factor.frag'
	ctx = moderngl.create_standalone_context()
	prog = ctx.program(
		contents(vert_path),contents(frag_path))
	prog['iChannel0'] = 0
	tex = ctx.texture((w,h),3,hsv.tobytes(),dtype='f4')
	tex.use(0)
	prog['iChannel1'] = 1
	tex = ctx.texture((w,h),3,lab.tobytes(),dtype='f4')
	tex.use(1)
	uni = prog['iResolution']
	uni.value = (w,h,1)
	prog['factors'] = (
		factor_r,factor_y,factor_c,
		factor_g,factor_b,factor_m)
	col = ctx.texture((w,h),1,dtype='f4')
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
	img = img.reshape((h,w))
	return img