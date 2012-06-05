CC=cc
CFLAGS=-I../lib -Wall -ggdb
LDFLAGS=-L../lib ../lib/libmosquitto.so.1
INSTALL=install
prefix=/usr/local

.PHONY: all install uninstall clean

all : mosquitto_control

mosquitto_control : control_client.o
	${CC} $^ -o $@ ${LDFLAGS}

install : all
	$(INSTALL) -d ${DESTDIR}$(prefix)/bin
	$(INSTALL) -s mosquitto_control ${DESTDIR}${prefix}/bin/mosquitto_control

uninstall :
	-rm -f ${DESTDIR}${prefix}/bin/mosquitto_control

clean : 
	-rm -f *.o mosquitto_control
