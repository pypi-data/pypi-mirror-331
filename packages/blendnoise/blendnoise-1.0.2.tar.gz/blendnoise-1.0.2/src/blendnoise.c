#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "bli_noise.h"
#include "blender_shaders.h"

static PyObject *BlendNoiseError;

static PyObject *method_noise_generic_noise (PyObject *self, PyObject *args) {
	float noisesize;
	float x;
	float y;
	float z;
	int hard;
	int noisebasis;
	if (!PyArg_ParseTuple (args, "ffffpi", &noisesize, &x, &y, &z, &hard, &noisebasis)) {
		return NULL;
	}
	float result = BLI_noise_generic_noise (noisesize, x, y, z, hard, noisebasis);
	return Py_BuildValue ("f", result);
}

static PyObject *method_noise_generic_turbulence (PyObject *self, PyObject *args) {
	float noisesize;
	float x;
	float y;
	float z;
	int oct;
	int hard;
	int noisebasis;
	if (!PyArg_ParseTuple (args, "ffffipi", &noisesize, &x, &y, &z, &oct, &hard, &noisebasis)) {
		return NULL;
	}
	float result = BLI_noise_generic_turbulence (noisesize, x, y, z, oct, hard, noisebasis);
	return Py_BuildValue ("f", result);
}

static PyObject *method_noise_mg_fbm (PyObject *self, PyObject *args) {
	float x;
	float y;
	float z;
	float H;
	float lacunarity;
	float octaves;
	int noisebasis;
	if (!PyArg_ParseTuple (args, "ffffffi", &x, &y, &z, &H, &lacunarity, &octaves, &noisebasis)) {
		return NULL;
	}
	float result = BLI_noise_mg_fbm (x, y, z, H, lacunarity, octaves, noisebasis);
	return Py_BuildValue ("f", result);
}

static PyObject *method_noise_mg_multi_fractal (PyObject *self, PyObject *args) {
	float x;
	float y;
	float z;
	float H;
	float lacunarity;
	float octaves;
	int noisebasis;
	if (!PyArg_ParseTuple (args, "ffffffi", &x, &y, &z, &H, &lacunarity, &octaves, &noisebasis)) {
		return NULL;
	}
	float result = BLI_noise_mg_multi_fractal (x, y, z, H, lacunarity, octaves, noisebasis);
	return Py_BuildValue ("f", result);
}


static PyObject *method_noise_mg_hetero_terrain (PyObject *self, PyObject *args) {
	float x;
	float y;
	float z;
	float H;
	float lacunarity;
	float octaves;
	float offset;
	int noisebasis;
	if (!PyArg_ParseTuple (args, "fffffffi", &x, &y, &z, &H, &lacunarity, &octaves, &offset, &noisebasis)) {
		return NULL;
	}
	float result = BLI_noise_mg_hetero_terrain (x, y, z, H, lacunarity, octaves, offset, noisebasis);
	return Py_BuildValue ("f", result);
}

static PyObject *method_noise_mg_hybrid_multi_fractal (PyObject *self, PyObject *args) {
	float x;
	float y;
	float z;
	float H;
	float lacunarity;
	float octaves;
	float offset;
	float gain;
	int noisebasis;
	if (!PyArg_ParseTuple (args, "ffffffffi", &x, &y, &z, &H, &lacunarity, &octaves, &offset, &gain, &noisebasis)) {
		return NULL;
	}
	float result = BLI_noise_mg_hybrid_multi_fractal (x, y, z, H, lacunarity, octaves, offset, gain, noisebasis);
	return Py_BuildValue ("f", result);
}

static PyObject *method_noise_mg_ridged_multi_fractal (PyObject *self, PyObject *args) {
	float x;
	float y;
	float z;
	float H;
	float lacunarity;
	float octaves;
	float offset;
	float gain;
	int noisebasis;
	if (!PyArg_ParseTuple (args, "ffffffffi", &x, &y, &z, &H, &lacunarity, &octaves, &offset, &gain, &noisebasis)) {
		return NULL;
	}
	float result = BLI_noise_mg_ridged_multi_fractal (x, y, z, H, lacunarity, octaves, offset, gain, noisebasis);
	return Py_BuildValue ("f", result);
}

static PyObject *method_noise_mg_variable_lacunarity (PyObject *self, PyObject *args) {
	float x;
	float y;
	float z;
	float distortion;
	int noisebasis1;
	int noisebasis2;
	if (!PyArg_ParseTuple (args, "ffffii", &x, &y, &z, &distortion, &noisebasis1, &noisebasis2)) {
		return NULL;
	}
	float result = BLI_noise_mg_variable_lacunarity (x, y, z, distortion, noisebasis1, noisebasis2);
	return Py_BuildValue ("f", result);
}

static PyObject *method_node_tex_magic (PyObject *self, PyObject *args) {
	float x;
	float y;
	float z;
	float scale;
	float distortion;
	float depth;
	if (!PyArg_ParseTuple (args, "ffffff", &x, &y, &z, &scale, &distortion, &depth)) {
		return NULL;
	}
	float color [4];
	float result = node_tex_magic (x, y, z, scale, distortion, depth, color);
	return Py_BuildValue ("f", result);
}

// PACKAGE

static PyMethodDef methods [] = {
	{"noise", method_noise_generic_noise, METH_VARARGS, "Returns noise value from the noise basis at the position specified."},
	{"turbulence", method_noise_generic_turbulence, METH_VARARGS, "Returns the turbulence value from the noise basis at the specified position."},
	{"fbm", method_noise_mg_fbm, METH_VARARGS, "Returns the fractal Brownian motion (fBm) noise value from the noise basis at the specified position."},
	{"multi_fractal", method_noise_mg_multi_fractal, METH_VARARGS, "Returns multifractal noise value from the noise basis at the specified position."},
	{"hetero_terrain", method_noise_mg_hetero_terrain, METH_VARARGS, "Returns the heterogeneous terrain value from the noise basis at the specified position."},
	{"hybrid_multi_fractal", method_noise_mg_hybrid_multi_fractal, METH_VARARGS, "Returns hybrid multifractal value from the noise basis at the specified position."},
	{"ridged_multi_fractal", method_noise_mg_ridged_multi_fractal, METH_VARARGS, "Returns ridged multifractal value from the noise basis at the specified position."},
	{"variable_lacunarity", method_noise_mg_variable_lacunarity, METH_VARARGS, "Returns variable lacunarity noise value, a distorted variety of noise, from noise type 1 distorted by noise type 2 at the specified position."},
	{"magic_texture", method_node_tex_magic, METH_VARARGS, "Returns psychedelic magic texture."},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
	PyModuleDef_HEAD_INIT,
	"blendnoise",
	"Python wrapper for Blender noise functions",
	-1,
	methods
};

PyMODINIT_FUNC PyInit_blendnoise (void) {
	PyObject *m;
	m = PyModule_Create (&module);
	if (m == NULL)
		return NULL;
	BlendNoiseError = PyErr_NewException ("blendnoise.error", NULL, NULL);
	if (PyModule_AddObjectRef (m, "error", BlendNoiseError) < 0) {
		Py_CLEAR (BlendNoiseError);
		Py_DECREF (m);
		return NULL;
	}
	return m;
}
