from setuptools import setup, Extension

setup (
	name = 'blendnoise',
	version = '1.0.2',
	description = 'Python wrapper for Blender noise functions',
	long_description = open ('README.rst', 'rt').read (),
	maintainer = 'Ellie Viesná',
	maintainer_email = 'snowboard_refinery@proton.me',
	url = "https://codeberg.org/screwery/blendnoise",
	keywords = ['blender', 'noise', 'landscape', 'perlin', 'voronoi', 'cell', 'musgrave', 'fractal'],
	license = 'GNU GPLv2+',
	classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
			"Natural Language :: English",
			"Programming Language :: C",
			"Programming Language :: Python :: 3.11",
			"Programming Language :: Python :: 3.12",
			"Topic :: Artistic Software",
			"Topic :: Multimedia :: Graphics :: 3D Modeling"
		],
	ext_modules = [
		Extension (
			name = 'blendnoise',
			extra_link_args = ['-lm'],
			sources = ['src/bli_noise.c', 'src/blender_shaders.c', 'src/blendnoise.c'])
		]
	)
