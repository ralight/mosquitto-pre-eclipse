include ../config.mk

SOVERSION=1
ifneq ($(UNAME),SunOS)
	LINKER_VERSION:=-Wl,--version-script=linker.version
endif

.PHONY : really clean install

MOSQ_OBJS=mosquitto.o \
		  logging_mosq.o \
		  memory_mosq.o \
		  messages_mosq.o \
		  net_mosq.o \
		  read_handle.o \
		  read_handle_client.o \
		  read_handle_shared.o \
		  send_mosq.o \
		  send_client_mosq.o \
		  thread_mosq.o \
		  util_mosq.o \
		  will_mosq.o

all : libmosquitto.so.${SOVERSION} libmosquitto.a
	$(MAKE) -C cpp
	$(MAKE) -C python

install : all
	$(INSTALL) -d ${DESTDIR}$(prefix)/lib${LIB_SUFFIX}/
	$(INSTALL) libmosquitto.so.${SOVERSION} ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so.${SOVERSION}
	ln -sf libmosquitto.so.${SOVERSION} ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so
	$(INSTALL) -d ${DESTDIR}${prefix}/include/
	$(INSTALL) mosquitto.h ${DESTDIR}${prefix}/include/mosquitto.h
	$(MAKE) -C cpp install
	$(MAKE) -C python install

uninstall :
	-rm -f ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so.${SOVERSION}
	-rm -f ${DESTDIR}${prefix}/lib${LIB_SUFFIX}/libmosquitto.so
	-rm -f ${DESTDIR}${prefix}/include/mosquitto.h

reallyclean : clean

clean :
	-rm -f *.o libmosquitto.so.${SOVERSION} libmosquitto.so libmosquitto.a
	$(MAKE) -C cpp clean
	$(MAKE) -C python clean

libmosquitto.so.${SOVERSION} : ${MOSQ_OBJS}
	$(CC) -shared $(LINKER_VERSION) -Wl,-soname,libmosquitto.so.${SOVERSION} $^ -o $@ ${LIB_LIBS}

libmosquitto.a : ${MOSQ_OBJS}
	$(AR) cr $@ $^
mosquitto.o : mosquitto.c mosquitto.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

logging_mosq.o : logging_mosq.c logging_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

messages_mosq.o : messages_mosq.c messages_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

memory_mosq.o : memory_mosq.c memory_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

net_mosq.o : net_mosq.c net_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

read_handle.o : read_handle.c read_handle.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

read_handle_client.o : read_handle_client.c read_handle.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

read_handle_shared.o : read_handle_shared.c read_handle.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

send_mosq.o : send_mosq.c send_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

send_client_mosq.o : send_client_mosq.c send_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

thread_mosq.o : thread_mosq.c
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

util_mosq.o : util_mosq.c util_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

will_mosq.o : will_mosq.c will_mosq.h
	$(CC) $(LIB_CFLAGS) -fPIC -c $< -o $@

