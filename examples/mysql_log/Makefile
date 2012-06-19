CFLAGS=-Wall -ggdb
LDFLAGS=-lmosquitto -lmysqlclient

.PHONY: all clean

all : mosquitto_mysql_log

mosquitto_mysql_log : mysql_log.o
	${CC} $^ -o $@ ${LDFLAGS}

clean : 
	-rm -f *.o mosquitto_mysql_log
