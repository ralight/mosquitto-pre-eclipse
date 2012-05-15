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
	./02-subscribe-qos0.py c/02-subscribe-qos0.test
	./02-subscribe-qos0.py cpp/02-subscribe-qos0.test
	./02-subscribe-qos0.py python/02-subscribe-qos0.py
	./02-subscribe-qos1.py c/02-subscribe-qos1.test
	./02-subscribe-qos1.py cpp/02-subscribe-qos1.test
	./02-subscribe-qos1.py python/02-subscribe-qos1.py
	./02-subscribe-qos2.py c/02-subscribe-qos2.test
	./02-subscribe-qos2.py cpp/02-subscribe-qos2.test
	./02-subscribe-qos2.py python/02-subscribe-qos2.py
	./02-unsubscribe.py c/02-unsubscribe.test
	./02-unsubscribe.py cpp/02-unsubscribe.test
	./02-unsubscribe.py python/02-unsubscribe.py

clean : 
	$(MAKE) -C c clean
	$(MAKE) -C cpp clean
