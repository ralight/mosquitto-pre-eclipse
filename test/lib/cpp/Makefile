.PHONY: all test 01

CFLAGS=-I../../../lib/cpp -DDEBUG
LIBS=../../../lib/libmosquitto.so.1 ../../../lib/cpp/libmosquittopp.so.1

all : 01 02 03

01-con-discon-success.test : 01-con-discon-success.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01-will-set.test : 01-will-set.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01-unpwd-set.test : 01-unpwd-set.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01-will-unpwd-set.test : 01-will-unpwd-set.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01-no-clean-session.test : 01-no-clean-session.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01-keepalive-pingreq.test : 01-keepalive-pingreq.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

02-subscribe-qos0.test : 02-subscribe-qos0.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

02-subscribe-qos1.test : 02-subscribe-qos1.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

02-subscribe-qos2.test : 02-subscribe-qos2.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

02-unsubscribe.test : 02-unsubscribe.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-qos0.test : 03-publish-qos0.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-qos0-no-payload.test : 03-publish-qos0-no-payload.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-c2b-qos1-timeout.test : 03-publish-c2b-qos1-timeout.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-c2b-qos2-timeout.test : 03-publish-c2b-qos2-timeout.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-b2c-qos1.test : 03-publish-b2c-qos1.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-b2c-qos2.test : 03-publish-b2c-qos2.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01 : 01-con-discon-success.test 01-will-set.test 01-unpwd-set.test 01-will-unpwd-set.test 01-no-clean-session.test 01-keepalive-pingreq.test

02 : 02-subscribe-qos0.test 02-subscribe-qos1.test 02-subscribe-qos2.test 02-unsubscribe.test

03 : 03-publish-qos0.test 03-publish-qos0-no-payload.test 03-publish-c2b-qos1-timeout.test 03-publish-c2b-qos2-timeout.test 03-publish-b2c-qos1.test 03-publish-b2c-qos2.test

clean :
	rm -f *.test
