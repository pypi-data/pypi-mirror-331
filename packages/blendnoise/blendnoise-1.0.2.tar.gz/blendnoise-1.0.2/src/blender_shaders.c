#include "blender_shaders.h"

static const float FLOAT_PI = 3.14159265358979323846f;

float node_tex_magic (float co_x, float co_y, float co_z, float scale, float distortion, float depth, float color [4]) {
	float p_x = fmod (co_x * scale, 2.0f * FLOAT_PI);
	float p_y = fmod (co_y * scale, 2.0f * FLOAT_PI);
	float p_z = fmod (co_z * scale, 2.0f * FLOAT_PI);
	float x = sin ((p_x + p_y + p_z) * 5.0f);
	float y = cos((-p_x + p_y - p_z) * 5.0f);
	float z = -cos((-p_x - p_y + p_z) * 5.0f);
	if (depth > 0) {
		x *= distortion;
		y *= distortion;
		z *= distortion;
		y = -cos (x - y + z);
		y *= distortion;
		if (depth > 1) {
			x = cos (x - y - z);
			x *= distortion;
			if (depth > 2) {
				z = sin (-x - y - z);
				z *= distortion;
				if (depth > 3) {
					x = -cos (-x + y - z);
					x *= distortion;
					if (depth > 4) {
						y = -sin (-x + y + z);
						y *= distortion;
						if (depth > 5) {
							y = -cos (-x + y + z);
							y *= distortion;
							if (depth > 6) {
								x = cos (x + y + z);
								x *= distortion;
								if (depth > 7) {
									z = sin (x + y - z);
									z *= distortion;
									if (depth > 8) {
										x = -cos (-x - y + z);
										x *= distortion;
										if (depth > 9) {
											y = -sin (x - y + z);
											y *= distortion;
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
	if (distortion != 0.0f) {
		distortion *= 2.0f;
		x /= distortion;
		y /= distortion;
		z /= distortion;
	}
	color [0] = 0.5f - x;
	color [1] = 0.5f - y;
	color [2] = 0.5f - z;
	color [3] = 1.0f;
	return (color [0] + color [1] + color [1]) / 3.0f;
}
