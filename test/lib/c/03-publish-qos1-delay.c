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
	}else{
		mosquitto_publish(mosq, NULL, "pub/qos1/test", strlen("message"), "message", 1, false);
	}
}

void on_publish(struct mosquitto *mosq, void *obj, uint16_t mid)
{
	mosquitto_disconnect(mosq);
}

void on_disconnect(struct mosquitto *mosq, void *obj, int rc)
{
	run = 0;
	printf("on_disco\n");
}

int main(int argc, char *argv[])
{
	int rc;
	struct mosquitto *mosq;

	mosquitto_lib_init();

	mosq = mosquitto_new("publish-qos1-test", true, NULL);
	mosquitto_connect_callback_set(mosq, on_connect);
	mosquitto_disconnect_callback_set(mosq, on_disconnect);
	mosquitto_publish_callback_set(mosq, on_publish);
	mosquitto_message_retry_set(mosq, 3);

	rc = mosquitto_connect(mosq, "localhost", 1888, 60);

	while(run == -1){
		mosquitto_loop(mosq, 300);
	}

	mosquitto_lib_cleanup();
	printf("end\n");
	return run;
}
