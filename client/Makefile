SOVERSION=1
CC=cc
CFLAGS=-I../lib -Wall -ggdb
LDFLAGS=-L../lib ../lib/libmosquitto.so.${SOVERSION}
INSTALL=install
prefix=/usr/local

.PHONY: all install uninstall reallyclean clean

all : mosquitto_pub mosquitto_sub

mosquitto_pub : pub_client.o ../lib/libmosquitto.so.${SOVERSION}
	${CC} $< -o $@ ${LDFLAGS}

mosquitto_sub : sub_client.o ../lib/libmosquitto.so.${SOVERSION}
	${CC} $< -o $@ ${LDFLAGS}

../lib/libmosquitto.so.${SOVERSION} :
	$(MAKE) -C ../lib

install : all
	$(INSTALL) -d ${DESTDIR}$(prefix)/bin
	$(INSTALL) -s mosquitto_pub ${DESTDIR}${prefix}/bin/mosquitto_pub
	$(INSTALL) -s mosquitto_sub ${DESTDIR}${prefix}/bin/mosquitto_sub

uninstall :
	-rm -f ${DESTDIR}${prefix}/bin/mosquitto_pub
	-rm -f ${DESTDIR}${prefix}/bin/mosquitto_sub

reallyclean : clean

clean : 
	-rm -f *.o mosquitto_pub mosquitto_sub
