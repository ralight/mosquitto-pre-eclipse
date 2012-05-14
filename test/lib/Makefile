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
	./01-will-set.py c/01-will-set.test
	./01-will-set.py cpp/01-will-set.test
	./01-will-set.py python/01-will-set.py
	./01-unpwd-set.py c/01-unpwd-set.test
	./01-unpwd-set.py cpp/01-unpwd-set.test
	./01-unpwd-set.py python/01-unpwd-set.py

clean : 
	$(MAKE) -C c clean
	$(MAKE) -C cpp clean
