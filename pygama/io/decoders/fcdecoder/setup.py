from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy
import sys

if sys.platform.startswith('freebsd'):
  print("Free BSD not support.")
  sys.exit(1)
elif sys.platform.startswith('linux'):
  print("Linking Linux fcio and tmio.")
  extra_objects = ["src/fcio_linux.a", "src/tmio-0.93_linux.a"]
elif sys.platform.startswith('darwin'):
  print("Linking Mac OS fcio and tmio.")
  extra_objects = ["src/fcio_mac.a", "src/tmio-0.93_mac.a"]
elif sys.platform.startswith('win32'):
  print("Windows not support.")
  sys.exit(1)

ext_modules = [Extension("fcutils",
                         sources = ["fcutils.pyx"],
                         include_dirs=["src", numpy.get_include()],
                         language='c',
                         # extra_objects=["src/fcio.a", "src/tmio-0.93.a", "src/fclayout.so"]
                         extra_objects=extra_objects
              )]

setup(
   name = "fcutils",
   ext_modules = cythonize(ext_modules)
)
