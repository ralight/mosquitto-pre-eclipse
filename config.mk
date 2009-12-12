VERSION=0.2
BUILDDATE=20091204

#MANCOUNTRIES=en_GB

CFLAGS=-I. -I.. -ggdb -Wall -Os
LDFLAGS=-nopie -lsqlite3 -lwrap

CC=gcc
INSTALL=install
XGETTEXT=xgettext
MSGMERGE=msgmerge
MSGFMT=msgfmt
DOCBOOK2MAN=docbook2man.pl

prefix=/usr/local
mandir=${prefix}/share/man
localedir=${prefix}/share/locale
