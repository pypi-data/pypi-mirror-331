#version 330

vec2 fragCoord = gl_FragCoord.xy;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform vec3 iChannelResolution[2];

out float fragColor;

float lerp(float x, float f0, float f1)
{
	float fx = (1-x)*f0+x*f1;
	return fx;
}

float lookup(int x)
{
	vec2 uv = vec2(x+0.5,0.5)/iChannelResolution[1].xy;
	return texture(iChannel1,uv).r;
}

void main()
{
	vec2 uv = fragCoord/iChannelResolution[0].xy;
	float h = texture(iChannel0,uv).r;
	int w = int(iChannelResolution[1].x);
	int x0 = int(min(floor(h/360*w),w-1));
	int x1 = int(min(ceil(h/360*w),w-1));
	float f0 = lookup(x0);
	float f1 = lookup(x1);
	float res = lerp(h/360,f0,f1);
	fragColor = res;
}