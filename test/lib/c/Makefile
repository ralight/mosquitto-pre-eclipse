.PHONY: all test 01 02 03 04

CFLAGS=-I../../../lib
LIBS=../../../lib/libmosquitto.so.1

all : 01 02 03 04

01-con-discon-success.test : 01-con-discon-success.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

01-will-set.test : 01-will-set.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

01-unpwd-set.test : 01-unpwd-set.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

01-will-unpwd-set.test : 01-will-unpwd-set.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

01-no-clean-session.test : 01-no-clean-session.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

01-keepalive-pingreq.test : 01-keepalive-pingreq.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

02-subscribe-qos0.test : 02-subscribe-qos0.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

02-subscribe-qos1.test : 02-subscribe-qos1.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

02-subscribe-qos2.test : 02-subscribe-qos2.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

02-unsubscribe.test : 02-unsubscribe.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-qos0.test : 03-publish-qos0.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-qos0-no-payload.test : 03-publish-qos0-no-payload.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-c2b-qos1-timeout.test : 03-publish-c2b-qos1-timeout.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-c2b-qos2-timeout.test : 03-publish-c2b-qos2-timeout.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-b2c-qos1.test : 03-publish-b2c-qos1.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

03-publish-b2c-qos2.test : 03-publish-b2c-qos2.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

04-retain-qos0.test : 04-retain-qos0.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

01 : 01-con-discon-success.test 01-will-set.test 01-unpwd-set.test 01-will-unpwd-set.test 01-no-clean-session.test 01-keepalive-pingreq.test

02 : 02-subscribe-qos0.test 02-subscribe-qos1.test 02-subscribe-qos2.test 02-unsubscribe.test

03 : 03-publish-qos0.test 03-publish-qos0-no-payload.test 03-publish-c2b-qos1-timeout.test 03-publish-c2b-qos2-timeout.test 03-publish-b2c-qos1.test 03-publish-b2c-qos2.test

04 : 04-retain-qos0.test

clean :
	rm -f *.test
