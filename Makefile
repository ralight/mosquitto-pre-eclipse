include config.mk

DIRS=lib client src
DOCDIRS=man
DISTDIRS=man

.PHONY : all mosquitto docs binary clean reallyclean test install uninstall dist sign copy

all : mosquitto docs

docs :
	for d in ${DOCDIRS}; do $(MAKE) -C $${d}; done

binary : mosquitto

mosquitto :
	for d in ${DIRS}; do $(MAKE) -C $${d}; done

clean :
	for d in ${DIRS}; do $(MAKE) -C $${d} clean; done
	for d in ${DOCDIRS}; do $(MAKE) -C $${d} clean; done
	make -C test clean

reallyclean : 
	for d in ${DIRS}; do $(MAKE) -C $${d} reallyclean; done
	for d in ${DOCDIRS}; do $(MAKE) -C $${d} reallyclean; done
	make -C test reallyclean
	-rm -f *.orig

test : all
	$(MAKE) -C test test

install : mosquitto
	@for d in ${DIRS}; do $(MAKE) -C $${d} install; done
	@for d in ${DOCDIRS}; do $(MAKE) -C $${d} install; done
	$(INSTALL) -d ${DESTDIR}/etc/mosquitto
	$(INSTALL) -m 644 mosquitto.conf ${DESTDIR}/etc/mosquitto/mosquitto.conf
	$(INSTALL) -m 644 aclfile.example ${DESTDIR}/etc/mosquitto/aclfile.example
	$(INSTALL) -m 644 pwfile.example ${DESTDIR}/etc/mosquitto/pwfile.example

uninstall :
	@for d in ${DIRS}; do $(MAKE) -C $${d} uninstall; done

dist : reallyclean
	@for d in ${DISTDIRS}; do $(MAKE) -C $${d} dist; done
	
	mkdir -p dist/mosquitto-${VERSION}
	cp -r client examples installer lib logo man misc security service src test ChangeLog.txt CMakeLists.txt COPYING Makefile compiling.txt config.h config.mk readme.txt readme-windows.txt mosquitto.conf aclfile.example pwfile.example dist/mosquitto-${VERSION}/
	cd dist; tar -zcf mosquitto-${VERSION}.tar.gz mosquitto-${VERSION}/
	for m in man/*.xml; \
		do \
		hfile=$$(echo $${m} | sed -e 's#man/\(.*\)\.xml#\1#' | sed -e 's/\./-/g'); \
		$(XSLTPROC) $(DB_HTML_XSL) $${m} > dist/$${hfile}.html; \
	done


sign : dist
	cd dist; gpg --detach-sign -a mosquitto-${VERSION}.tar.gz

copy : sign
	cd dist; scp mosquitto-${VERSION}.tar.gz mosquitto-${VERSION}.tar.gz.asc mosquitto:mosquitto.org/files/source/
	cd dist; scp *.html mosquitto:mosquitto.org/man/
	scp ChangeLog.txt mosquitto:mosquitto.org/

