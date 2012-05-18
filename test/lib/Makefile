.PHONY: all test test-compile-c test-c test-compile-cpp test-cpp test-python
.NOTPARALLEL:

LD_LIBRARY_PATH=../../lib

all :

test : test-c test-cpp test-python

test-compile-c : 
	$(MAKE) -C c

test-compile-cpp : 
	$(MAKE) -C cpp

test-c : test-compile-c
	./01-con-discon-success.py c/01-con-discon-success.test
	./01-will-set.py c/01-will-set.test
	./01-unpwd-set.py c/01-unpwd-set.test
	./01-will-unpwd-set.py c/01-will-unpwd-set.test
	./01-no-clean-session.py c/01-no-clean-session.test
	./01-keepalive-pingreq.py c/01-keepalive-pingreq.test
	./02-subscribe-qos0.py c/02-subscribe-qos0.test
	./02-subscribe-qos1.py c/02-subscribe-qos1.test
	./02-subscribe-qos2.py c/02-subscribe-qos2.test
	./02-unsubscribe.py c/02-unsubscribe.test
	./03-publish-qos0.py c/03-publish-qos0.test
	./03-publish-qos0-no-payload.py c/03-publish-qos0-no-payload.test
	./03-publish-c2b-qos1-timeout.py c/03-publish-c2b-qos1-timeout.test
	./03-publish-c2b-qos2-timeout.py c/03-publish-c2b-qos2-timeout.test

test-cpp : test-compile-cpp
	./01-con-discon-success.py cpp/01-con-discon-success.test
	./01-will-set.py cpp/01-will-set.test
	./01-unpwd-set.py cpp/01-unpwd-set.test
	./01-will-unpwd-set.py cpp/01-will-unpwd-set.test
	./01-no-clean-session.py cpp/01-no-clean-session.test
	./01-keepalive-pingreq.py cpp/01-keepalive-pingreq.test
	./02-subscribe-qos0.py cpp/02-subscribe-qos0.test
	./02-subscribe-qos1.py cpp/02-subscribe-qos1.test
	./02-subscribe-qos2.py cpp/02-subscribe-qos2.test
	./02-unsubscribe.py cpp/02-unsubscribe.test
	./03-publish-qos0.py cpp/03-publish-qos0.test
	./03-publish-qos0-no-payload.py cpp/03-publish-qos0-no-payload.test
	./03-publish-c2b-qos1-timeout.py cpp/03-publish-c2b-qos1-timeout.test
	./03-publish-c2b-qos2-timeout.py cpp/03-publish-c2b-qos2-timeout.test

test-python :
	./01-con-discon-success.py python/01-con-discon-success.py
	./01-will-set.py python/01-will-set.py
	./01-unpwd-set.py python/01-unpwd-set.py
	./01-will-unpwd-set.py python/01-will-unpwd-set.py
	./01-no-clean-session.py python/01-no-clean-session.py
	./01-keepalive-pingreq.py python/01-keepalive-pingreq.py
	./02-subscribe-qos0.py python/02-subscribe-qos0.py
	./02-subscribe-qos1.py python/02-subscribe-qos1.py
	./02-subscribe-qos2.py python/02-subscribe-qos2.py
	./02-unsubscribe.py python/02-unsubscribe.py
	./03-publish-qos0.py python/03-publish-qos0.py
	./03-publish-qos0-no-payload.py python/03-publish-qos0-no-payload.py
	./03-publish-c2b-qos1-timeout.py python/03-publish-c2b-qos1-timeout.py
	./03-publish-c2b-qos2-timeout.py python/03-publish-c2b-qos2-timeout.py

clean : 
	$(MAKE) -C c clean
	$(MAKE) -C cpp clean
