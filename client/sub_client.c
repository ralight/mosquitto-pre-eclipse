/*
Copyright (c) 2009,2010, Roger Light <roger@atchoo.org>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of mosquitto nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <mosquitto.h>

static char **topics = NULL;
static int topic_count = 0;
static int topic_qos = 0;
int verbose = 0;
static struct mosquitto *mosq = NULL;

void my_message_callback(void *obj, struct mosquitto_message *message)
{
	if(verbose){
		if(message->payloadlen){
			printf("%s %s\n", message->topic, message->payload);
		}else{
			printf("%s (null)\n", message->topic);
		}
		fflush(stdout);
	}else{
		if(message->payloadlen){
			printf("%s\n", message->payload);
			fflush(stdout);
		}
	}
}

void my_connect_callback(void *obj, int result)
{
	int i;
	if(!result){
		for(i=0; i<topic_count; i++){
			mosquitto_subscribe(mosq, topics[i], topic_qos);
		}
	}else{
		fprintf(stderr, "Connect failed\n");
	}
}

void my_subscribe_callback(void *obj, uint16_t mid, int qos_count, uint8_t *granted_qos)
{
	int i;

	printf("Subscribed (mid: %d): %d", mid, granted_qos[0]);
	for(i=1; i<qos_count; i++){
		printf(", %d", granted_qos[i]);
	}
	printf("\n");
	free(granted_qos);
}

void print_usage(void)
{
	printf("mosquitto_sub is a simple mqtt client that will subscribe to a single topic and print all messages it receives.\n\n");
	printf("Usage: mosquitto_sub [-c] [-i id] [-k keepalive] [-p port] [-q qos] [-v] -t topic ...\n");
	printf("                     [--will-topic [--will-payload payload] [--will-qos qos] [--will-retain]]\n\n");
	printf(" -c : disable 'clean session' (store subscription and pending messages when client disconnects).\n");
	printf(" -d : enable debug messages.\n");
	printf(" -h : mqtt host to connect to. Defaults to localhost.\n");
	printf(" -i : id to use for this client. Defaults to mosquitto_sub_ appended with the process id.\n");
	printf(" -k : keep alive in seconds for this client. Defaults to 60.\n");
	printf(" -p : network port to connect to. Defaults to 1883.\n");
	printf(" -q : quality of service level to use for the subscription. Defaults to 0.\n");
	printf(" -t : mqtt topic to subscribe to. May be repeated multiple times.\n");
	printf(" -v : print published messages verbosely.\n");
	printf(" --will-payload : payload for the client Will, which is sent by the broker in case of\n");
	printf("                  unexpected disconnection. If not given and will-topic is set, a zero\n");
	printf("                  length message will be sent.\n");
	printf(" --will-qos : QoS level for the client Will.\n");
	printf(" --will-retain : if given, make the client Will retained.\n");
	printf(" --will-topic : the topic on which to publish the client Will.\n");
}

int main(int argc, char *argv[])
{
	char id[30];
	int i;
	char *host = "localhost";
	int port = 1883;
	int keepalive = 60;
	bool clean_session = true;
	bool debug = false;
	
	uint8_t *will_payload = NULL;
	long will_payloadlen = 0;
	int will_qos = 0;
	bool will_retain = false;
	char *will_topic = NULL;
	struct timespec timeout;

	sprintf(id, "mosquitto_sub_%d", getpid());

	for(i=1; i<argc; i++){
		if(!strcmp(argv[i], "-p") || !strcmp(argv[i], "--port")){
			if(i==argc-1){
				fprintf(stderr, "Error: -p argument given but no port specified.\n\n");
				print_usage();
				return 1;
			}else{
				port = atoi(argv[i+1]);
				if(port<1 || port>65535){
					fprintf(stderr, "Error: Invalid port given: %d\n", port);
					print_usage();
					return 1;
				}
			}
			i++;
		}else if(!strcmp(argv[i], "-c") || !strcmp(argv[i], "--disable-clean-session")){
			clean_session = false;
		}else if(!strcmp(argv[i], "-d") || !strcmp(argv[i], "--debug")){
			debug = true;
		}else if(!strcmp(argv[i], "-h") || !strcmp(argv[i], "--host")){
			if(i==argc-1){
				fprintf(stderr, "Error: -h argument given but no host specified.\n\n");
				print_usage();
				return 1;
			}else{
				host = argv[i+1];
			}
			i++;
		}else if(!strcmp(argv[i], "-i") || !strcmp(argv[i], "--id")){
			if(i==argc-1){
				fprintf(stderr, "Error: -i argument given but no id specified.\n\n");
				print_usage();
				return 1;
			}else{
				memset(id, 0, 30);
				snprintf(id, 29, "%s", argv[i+1]);
			}
			i++;
		}else if(!strcmp(argv[i], "-k") || !strcmp(argv[i], "--keepalive")){
			if(i==argc-1){
				fprintf(stderr, "Error: -k argument given but no keepalive specified.\n\n");
				print_usage();
				return 1;
			}else{
				keepalive = atoi(argv[i+1]);
				if(keepalive>65535){
					fprintf(stderr, "Error: Invalid keepalive given: %d\n", keepalive);
					print_usage();
					return 1;
				}
			}
			i++;
		}else if(!strcmp(argv[i], "-q") || !strcmp(argv[i], "--qos")){
			if(i==argc-1){
				fprintf(stderr, "Error: -q argument given but no QoS specified.\n\n");
				print_usage();
				return 1;
			}else{
				topic_qos = atoi(argv[i+1]);
				if(topic_qos<0 || topic_qos>2){
					fprintf(stderr, "Error: Invalid QoS given: %d\n", topic_qos);
					print_usage();
					return 1;
				}
			}
			i++;
		}else if(!strcmp(argv[i], "-t") || !strcmp(argv[i], "--topic")){
			if(i==argc-1){
				fprintf(stderr, "Error: -t argument given but no topic specified.\n\n");
				print_usage();
				return 1;
			}else{
				topic_count++;
				topics = realloc(topics, topic_count*sizeof(char *));
				topics[topic_count-1] = argv[i+1];
			}
			i++;
		}else if(!strcmp(argv[i], "-v") || !strcmp(argv[i], "--verbose")){
			verbose = 1;
		}else if(!strcmp(argv[i], "--will-payload")){
			if(i==argc-1){
				fprintf(stderr, "Error: --will-payload argument given but no will payload specified.\n\n");
				print_usage();
				return 1;
			}else{
				will_payload = (uint8_t *)argv[i+1];
				will_payloadlen = strlen((char *)will_payload);
			}
			i++;
		}else if(!strcmp(argv[i], "--will-qos")){
			if(i==argc-1){
				fprintf(stderr, "Error: --will-qos argument given but no will QoS specified.\n\n");
				print_usage();
				return 1;
			}else{
				will_qos = atoi(argv[i+1]);
				if(will_qos < 0 || will_qos > 2){
					fprintf(stderr, "Error: Invalid will QoS %d.\n\n", will_qos);
					return 1;
				}
			}
			i++;
		}else if(!strcmp(argv[i], "--will-retain")){
			will_retain = true;
		}else if(!strcmp(argv[i], "--will-topic")){
			if(i==argc-1){
				fprintf(stderr, "Error: --will-topic argument given but no will topic specified.\n\n");
				print_usage();
				return 1;
			}else{
				will_topic = argv[i+1];
			}
			i++;
		}else{
			fprintf(stderr, "Error: Unknown option '%s'.\n",argv[i]);
			print_usage();
			return 1;
		}
	}
	if(topic_count == 0){
		fprintf(stderr, "Error: You must specify a topic to subscribe to.\n");
		print_usage();
		return 1;
	}
	if(will_payload && !will_topic){
		fprintf(stderr, "Error: Will payload given, but no will topic given.\n");
		print_usage();
		return 1;
	}
	if(will_retain && !will_topic){
		fprintf(stderr, "Error: Will retain given, but no will topic given.\n");
		print_usage();
		return 1;
	}
	mosq = mosquitto_new(NULL, id);
	if(!mosq){
		fprintf(stderr, "Error: Out of memory.\n");
		return 1;
	}
	if(debug){
		mosquitto_log_init(mosq, MOSQ_LOG_DEBUG | MOSQ_LOG_ERR | MOSQ_LOG_WARNING
				| MOSQ_LOG_NOTICE | MOSQ_LOG_INFO, MOSQ_LOG_STDERR);
	}
	if(will_topic && mosquitto_will_set(mosq, true, will_topic, will_payloadlen, will_payload, will_qos, will_retain)){
		fprintf(stderr, "Error: Problem setting will.\n");
		return 1;
	}
	mosq->on_connect = my_connect_callback;
	mosq->on_message = my_message_callback;
	if(debug){
		mosq->on_subscribe = my_subscribe_callback;
	}

	if(mosquitto_connect(mosq, host, port, keepalive, clean_session)){
		fprintf(stderr, "Unable to connect.\n");
		return 1;
	}

	timeout.tv_sec = 0;
	timeout.tv_nsec = 50000000;
	while(!mosquitto_loop(mosq, &timeout)){
	}
	mosquitto_destroy(mosq);
	return 0;
}

