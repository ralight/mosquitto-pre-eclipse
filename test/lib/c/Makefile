.PHONY: all test 01

CFLAGS=-I../../../lib
LIBS=../../../lib/libmosquitto.so.1

all : 01

01-con-discon-success.test : 01-con-discon-success.c
	$(CC) $< -o $@ $(CFLAGS) $(LIBS)

01 : 01-con-discon-success.test

clean :
	rm -f *.test
