.PHONY: all test

all :

test :
	./run_broker.sh
	
	./01-connect-success.py
	./01-connect-invalid-protonum.py
	./01-connect-invalid-id-0.py
	./01-connect-invalid-id-30.py
	
	./kill_broker.sh
