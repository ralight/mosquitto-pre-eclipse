#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mosquitto.h>

static int run = -1;

void on_connect(struct mosquitto *mosq, void *obj, int rc)
{
	if(rc){
		exit(1);
	}
}

int main(int argc, char *argv[])
{
	int rc;
	struct mosquitto *mosq;

	mosquitto_lib_init();

	mosq = mosquitto_new("publish-qos2-test", true, NULL);
	mosquitto_connect_callback_set(mosq, on_connect);
	mosquitto_message_retry_set(mosq, 5);

	rc = mosquitto_connect(mosq, "localhost", 1888, 60);

	while(run == -1){
		mosquitto_loop(mosq, 300);
	}

	mosquitto_lib_cleanup();
	return run;
}
