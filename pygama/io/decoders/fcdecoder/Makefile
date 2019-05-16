default: setup.py
		/usr/bin/env python setup.py build_ext --inplace

install: default
		/usr/bin/env python setup.py install --user

clean: 
		rm -rf build
		rm fcutils.c
		rm fcutils.*.so
