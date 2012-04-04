.PHONY: all test

all :

test :
	./run_broker.sh
	
	./01-connect-success.py
	./01-connect-invalid-protonum.py
	
	./kill_broker.sh
