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
	./01-will-unpwd-set.py c/01-will-unpwd-set.test
	./01-will-unpwd-set.py cpp/01-will-unpwd-set.test
	./01-will-unpwd-set.py python/01-will-unpwd-set.py
	./01-no-clean-session.py c/01-no-clean-session.test
	./01-no-clean-session.py cpp/01-no-clean-session.test
	./01-no-clean-session.py python/01-no-clean-session.py

clean : 
	$(MAKE) -C c clean
	$(MAKE) -C cpp clean
