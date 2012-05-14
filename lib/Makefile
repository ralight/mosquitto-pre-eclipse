include ../config.mk

SOVERSION=1

.PHONY : really clean install

all : libmosquitto.so.${SOVERSION}
	make -C cpp
	make -C python

install : all
	$(INSTALL) -d ${DESTDIR}$(prefix)/lib${LIB_SUFFIX}/
	$(INSTALL) libmosquitto.so.${SOVERSION} ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so.${SOVERSION}
	ln -sf libmosquitto.so.${SOVERSION} ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so
	$(INSTALL) -d ${DESTDIR}${prefix}/include/
	$(INSTALL) mosquitto.h ${DESTDIR}${prefix}/include/mosquitto.h
	make -C cpp install
	make -C python install

uninstall :
	-rm -f ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so.${SOVERSION}
	-rm -f ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so
	-rm -f ${DESTDIR}${prefix}/include/mosquitto.h

reallyclean : clean

clean :
	-rm -f *.o libmosquitto.so.${SOVERSION} libmosquitto.so
	make -C cpp clean
	make -C python clean

libmosquitto.so.${SOVERSION} : mosquitto.o logging_mosq.o memory_mosq.o messages_mosq.o net_mosq.o read_handle.o read_handle_client.o read_handle_shared.o send_mosq.o send_client_mosq.o thread_mosq.o util_mosq.o will_mosq.o
	$(CC) -shared -Wl,--version-script=linker.version -Wl,-soname,libmosquitto.so.${SOVERSION} $^ -o $@ ${LIBS} -lpthread

mosquitto.o : mosquitto.c mosquitto.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

logging_mosq.o : logging_mosq.c logging_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

messages_mosq.o : messages_mosq.c messages_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

memory_mosq.o : memory_mosq.c memory_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

net_mosq.o : net_mosq.c net_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

read_handle.o : read_handle.c read_handle.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

read_handle_client.o : read_handle_client.c read_handle.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

read_handle_shared.o : read_handle_shared.c read_handle.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

send_mosq.o : send_mosq.c send_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

send_client_mosq.o : send_client_mosq.c send_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

thread_mosq.o : thread_mosq.c
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

util_mosq.o : util_mosq.c util_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

will_mosq.o : will_mosq.c will_mosq.h
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

