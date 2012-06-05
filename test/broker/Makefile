.PHONY: all clean test

all :

clean : 

test :
	./01-connect-success.py
	./01-connect-invalid-protonum.py
	./01-connect-invalid-id-0.py
	./01-connect-anon-denied.py
	./01-connect-uname-no-password-denied.py
	./01-connect-uname-password-denied.py
	./01-connect-uname-password-success.py
	./02-subscribe-qos0.py
	./02-subscribe-qos1.py
	./02-subscribe-qos2.py
	./02-unsubscribe-qos0.py
	./02-unsubscribe-qos1.py
	./02-unsubscribe-qos2.py
	./03-publish-qos1.py
	./03-publish-qos2.py
	./03-publish-b2c-timeout-qos1.py
	./03-publish-c2b-timeout-qos2.py
	./03-publish-b2c-timeout-qos2.py
	./04-retain-qos0.py
	./04-retain-qos1-qos0.py
	./04-retain-qos0-clear.py
	./05-clean-session-qos1.py 
	./06-bridge-reconnect-local-out.py
	./07-will-qos0.py

# Tests for with WITH_STRICT_PROTOCOL defined
strict-test : 
	./01-connect-invalid-id-24.py
