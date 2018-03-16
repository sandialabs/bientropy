python=python

c_demo: ext/demo.c ext/bientropy.c ext/bientropy.h
	gcc -g -Wall ext/demo.c ext/bientropy.c -lgmp -lm -o c_demo

valgrind.xml:
	${python} setup.py build_ext --debug --force
	valgrind --xml=yes --xml-file=valgrind.xml ${python} -m bientropy.demo
