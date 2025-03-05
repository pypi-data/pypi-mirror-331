.. image:: https://codeberg.org/screwery/blendnoise/raw/branch/master/image.png
   :alt: Image

Description
-----------

.. image:: https://img.shields.io/pypi/v/blendnoise?style=flat-square
   :alt: PyPI - Version
.. image:: https://img.shields.io/pypi/pyversions/blendnoise?style=flat-square
   :alt: PyPI - Python Version
.. image:: https://img.shields.io/pypi/status/blendnoise?style=flat-square
   :alt: PyPI - Status
.. image:: https://img.shields.io/pypi/dm/blendnoise?style=flat-square
   :alt: PyPI - Downloads
.. image:: https://img.shields.io/pypi/l/blendnoise?style=flat-square
   :alt: PyPI - License
.. image:: https://img.shields.io/gitea/issues/open/screwery/blendnoise?gitea_url=https%3A%2F%2Fcodeberg.org&style=flat-square
   :alt: Gitea Issues
.. image:: https://img.shields.io/gitea/last-commit/screwery/blendnoise?gitea_url=https%3A%2F%2Fcodeberg.org&style=flat-square
   :alt: Gitea Last Commit

**blendnoise** is a Python wrapper for C-translated Blender noise functions described at `BLI_noise <https://projects.blender.org/blender/blender/src/commit/9cade06f5f62c9764c087b54345b7ca120656f09/source/blender/blenlib/BLI_noise.h>`_ module. It is distributed under the same conditions as Blender source code.

**WARNING:** The maintainer of this package is not connected in any way with Blender authors and/or developers.

Installation
------------

From PyPI
~~~~~~~~~

.. code:: bash

   python3 -m pip install blendnoise

From sources
~~~~~~~~~~~~

.. code:: bash

   python3 -m pip install build
   git clone https://codeberg.org/screwery/blendnoise
   cd blendnoise
   python3 -m build
   python3 -m pip install dist/*

You may need to install C compiler or that stuff.

Usage
-----

I’m not much of a Python C-extension coder, so all functions are C-styled and embarrasingly straightforward.

More info about those functions and arguments you can find at `official Blender docs <https://docs.blender.org/api/4.2/mathutils.noise.html>`_
or from `Blender sources <https://projects.blender.org/blender/blender/src/commit/9cade06f5f62c9764c087b54345b7ca120656f09/source/blender/blenlib/BLI_noise.h>`_
itself.

Also, you may find useful a fair Matplotlib `visualization script <https://codeberg.org/screwery/blendnoise/src/branch/master/visualization_example.py>`_.

.. code:: python3

   import blendnoise

   # use those ints for noisebasis
   NOISEBASIS = {
       'OriginalPerlin': 1,
       'NewPerlin': 2,
       'VoronoiF1': 3,
       'VoronoiF2': 4,
       'VoronoiF3': 5,
       'VoronoiF4': 6,
       'VoronoiF1F2': 7,
       'VoronoiCracked': 8,
       'Cell': 14,
       'Blender': 0
       }

   # Generic noise: just noisebasis, nothing more
   blendnoise.noise (noisesize: float, x: float, y: float, z: float, hard: bool,
                     noisebasis: int)

   # Generic turbulence
   blendnoise.turbulence (noisesize: float, x: float, y: float, z: float,
                          oct: int, hard: bool, noisebasis: int)

   # Fractal Brownian Movement (FBM)
   blendnoise.fbm (x: float, y: float, z: float, H: float, lacunarity: float,
                   octaves: float, noisebasis: int)

   # Multi Fractal
   blendnoise.multi_fractal (x: float, y: float, z: float, H: float,
                             lacunarity: float, octaves: float, noisebasis: int)

   # Heterogeneous Terrain
   blendnoise.hetero_terrain (x: float, y: float, z: float, H: float,
                              lacunarity: float, octaves: float, offset: float,
                              noisebasis: int)

   # Hybrid Multi Fractal
   blendnoise.hybrid_multi_fractal (x: float, y: float, z: float, H: float,
                                    lacunarity: float, octaves: float,
                                    offset: float, gain: float, noisebasis: int)

   # Ridged Multi Fractal
   blendnoise.ridged_multi_fractal (x: float, y: float, z: float, H: float,
                                    lacunarity: float, octaves: float, offset:
                                    float, gain: float, noisebasis: int)

   # Variable Lacunarity: combined noise bases
   blendnoise.variable_lacunarity (x: float, y: float, z: float, distortion: float,
                                   noisebasis1: int, noisebasis2: int)

   # Magic Texture (Blender shader texture)
   blendnoise.magic_texture (x: float, y: float, z: float, scale: float,
                             distortion: float, depth: float)

Bugs
----

Feel free to report bugs and request features `here <https://codeberg.org/screwery/blendnoise/issues>`_.
