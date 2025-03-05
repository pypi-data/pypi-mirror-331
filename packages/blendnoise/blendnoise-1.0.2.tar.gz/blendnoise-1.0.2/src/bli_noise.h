#ifndef BLI_NOISE_H
#define BLI_NOISE_H

#include <math.h>

// Perlin

float lerp (float t, float a, float b);
float npfade (float t);
float grad (int hash_val, float x, float y, float z);
float BLI_noise_hnoise (float noisesize, float x, float y, float z);
float BLI_noise_turbulence (float noisesize, float x, float y, float z, int nr);
float BLI_noise_hnoisep (float noisesize, float x, float y, float z);

// Voronoi

void BLI_noise_voronoi (float x, float y, float z, float *da, float *pa, float me, int dtype);

// Cell noise

float BLI_noise_cell (float x, float y, float z);
void BLI_noise_cell_v3 (float x, float y, float z, float r_ca [3]);

// API

float BLI_noise_generic_noise (float noisesize, float x, float y, float z, int hard, int noisebasis);
float BLI_noise_generic_turbulence (float noisesize, float x, float y, float z, int oct, int hard, int noisebasis);
float BLI_noise_mg_fbm (float x, float y, float z, float H, float lacunarity, float octaves, int noisebasis);
float BLI_noise_mg_multi_fractal (float x, float y, float z, float H, float lacunarity, float octaves, int noisebasis);
float BLI_noise_mg_hetero_terrain (float x, float y, float z, float H, float lacunarity, float octaves, float offset, int noisebasis);
float BLI_noise_mg_hybrid_multi_fractal (float x, float y, float z, float H, float lacunarity, float octaves, float offset, float gain, int noisebasis);
float BLI_noise_mg_ridged_multi_fractal (float x, float y, float z, float H, float lacunarity, float octaves, float offset, float gain, int noisebasis);
float BLI_noise_mg_variable_lacunarity (float x, float y, float z, float distortion, int nbas1, int nbas2);

#endif // BLI_NOISE_H
