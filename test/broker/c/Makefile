.PHONY: all test clean reallyclean

CFLAGS=-I../../../lib -I../../../src -Wall -Werror

all : auth_plugin.so

auth_plugin.so : auth_plugin.c
	$(CC) ${CFLAGS} -fPIC -shared $^ -o $@ 


reallyclean : clean
	-rm -f *.orig

clean :
	rm -f *.so
