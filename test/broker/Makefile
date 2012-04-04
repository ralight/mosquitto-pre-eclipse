.PHONY: all test

all :

test :
	./run_broker.sh
	
	./01-connect-success.py
	./01-connect-invalid-protonum.py
	./01-connect-invalid-id-0.py
	./01-connect-invalid-id-30.py
	./02-subscribe-qos0.py
	./02-subscribe-qos1.py
	./02-subscribe-qos2.py
	
	./kill_broker.sh

test-kill:
	./kill_broker.sh
