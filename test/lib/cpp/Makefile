.PHONY: all test 01

CFLAGS=-I../../../lib/cpp
LIBS=../../../lib/cpp/libmosquittopp.so.1 ../../../lib/libmosquitto.so.1

all : 01

01-con-discon-success.test : 01-con-discon-success.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01-will-set.test : 01-will-set.cpp
	$(CXX) $< -o $@ $(CFLAGS) $(LIBS)

01 : 01-con-discon-success.test 01-will-set.test

clean :
	rm -f *.test
