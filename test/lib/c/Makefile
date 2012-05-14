.PHONY: all test 01

CFLAGS=-I../../../lib
LIBS=../../../lib/libmosquitto.so.1

all : 01

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

01 : 01-con-discon-success.test 01-will-set.test 01-unpwd-set.test 01-will-unpwd-set.test 01-no-clean-session.test

clean :
	rm -f *.test
