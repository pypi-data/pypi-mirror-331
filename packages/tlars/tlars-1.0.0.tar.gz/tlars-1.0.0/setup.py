from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import setuptools
import numpy as np

__version__ = '1.0.0'

# Detect platform
is_windows = sys.platform.startswith('win')

# Define the extension module
ext_modules = [
    Extension(
        'tlars.tlars_cpp',
        ['src/tlars_cpp.cpp', 'src/tlars_cpp_pybind.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            os.path.join(os.path.dirname(__file__), 'pybind11/include'),
            # Path to carma headers
            os.path.join(os.path.dirname(__file__), 'carma/include'),
            # Path to Armadillo headers - may need to be adjusted
            '/usr/include',  # Linux default
            # Path to src directory for header files
            os.path.join(os.path.dirname(__file__), 'src'),
            # NumPy headers
            np.get_include(),
        ],
        language='c++',
        extra_compile_args=['-std=c++14'],
        extra_link_args=['-larmadillo'] if not is_windows else [],
    ),
]

# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True

# A custom build extension for dealing with C++14 compiler requirements
class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    if sys.platform == 'darwin':
        darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.7']
        c_opts['unix'] += darwin_opts
        l_opts['unix'] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append('-std=c++14')
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args += opts
            ext.extra_link_args += link_opts
        build_ext.build_extensions(self)

setup(
    name='tlars',
    version=__version__,
    author='Arnau Vilella',
    author_email='avp@connect.ust.hk',
    url='https://github.com/author/tlars-python',
    description='Python port of the tlars R package by Jasin Machkour',
    long_description='',
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.6.0', 'numpy>=1.19.0'],
    setup_requires=['pybind11>=2.6.0', 'numpy>=1.19.0'],
    cmdclass={'build_ext': BuildExt},
    packages=['tlars'],
    zip_safe=False,
    python_requires='>=3.6',
) 