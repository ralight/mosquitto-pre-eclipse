.PHONY: all test-compile test

LD_LIBRARY_PATH=../../lib

all :

test-compile : 
	$(MAKE) -C c
	$(MAKE) -C cpp

test : test-compile
	./01-con-discon-success.py c/01-con-discon-success.test
	./01-con-discon-success.py cpp/01-con-discon-success.test
	./01-con-discon-success.py python/01-con-discon-success.py

clean : 
	$(MAKE) -C c clean
	$(MAKE) -C cpp clean
