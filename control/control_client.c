/*
Copyright (c) 2011 Roger Light <roger@atchoo.org>
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


#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef WIN32
#include <unistd.h>
#else
#include <process.h>
#define snprintf sprintf_s
#endif

#include <mosquitto.h>

static bool connected = true;
static char *username = NULL;
static char *password = NULL;

void my_connect_callback(void *obj, int result)
{
	if(!result){
		fprintf(stderr, "Connection succeeded.\n");
	}else{
		switch(result){
			case 1:
				fprintf(stderr, "Connection Refused: unacceptable protocol version\n");
				break;
			case 2:
				fprintf(stderr, "Connection Refused: identifier rejected\n");
				break;
			case 3:
				fprintf(stderr, "Connection Refused: broker unavailable\n");
				break;
			case 4:
				fprintf(stderr, "Connection Refused: bad user name or password\n");
				break;
			case 5:
				fprintf(stderr, "Connection Refused: not authorised\n");
				break;
			default:
				fprintf(stderr, "Connection Refused: unknown reason\n");
				break;
		}
	}
}

void my_disconnect_callback(void *obj)
{
	connected = false;
}

void my_publish_callback(void *obj, uint16_t mid)
{
}

void print_usage(void)
{
	printf("mosquitto_control is a simple mqtt client that will publish a message on a single topic and exit.\n\n");
	printf("Usage: mosquitto_control [-d] [-h host] [-i id] [-p port] [-q qos] [-r] {-f file | -l | -n | -m message} -t topic\n");
	printf("                     [-u username [--pw password]]\n\n");
	printf(" -d : enable debug messages.\n");
	printf(" -f : send the contents of a file as the message.\n");
	printf(" -h : mqtt host to connect to. Defaults to localhost.\n");
	printf(" -i : id to use for this client. Defaults to mosquitto_control_ appended with the process id.\n");
	printf(" -l : read messages from stdin, sending a separate message for each line.\n");
	printf(" -m : message payload to send.\n");
	printf(" -n : send a null (zero length) message.\n");
	printf(" -p : network port to connect to. Defaults to 1883.\n");
	printf(" -q : quality of service level to use for all messages. Defaults to 0.\n");
	printf(" -r : message should be retained.\n");
	printf(" -s : read message from stdin, sending the entire input as a message.\n");
	printf(" -t : mqtt topic to publish to.\n");
	printf(" -u : provide a username (requires MQTT 3.1 broker)\n");
	printf(" --pw : provide a password (requires MQTT 3.1 broker)\n");
	printf("\nSee http://mosquitto.org/ for more information.\n\n");
}

int main(int argc, char *argv[])
{
	char *id = NULL;
	int i;
	char *host = "localhost";
	int port = 1883;
	int keepalive = 60;
	bool debug = false;
	struct mosquitto *mosq = NULL;

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
				id = argv[i+1];
			}
			i++;
		}else if(!strcmp(argv[i], "-u") || !strcmp(argv[i], "--username")){
			if(i==argc-1){
				fprintf(stderr, "Error: -u argument given but no username specified.\n\n");
				print_usage();
				return 1;
			}else{
				username = argv[i+1];
			}
			i++;
		}else if(!strcmp(argv[i], "--pw")){
			if(i==argc-1){
				fprintf(stderr, "Error: --pw argument given but no password specified.\n\n");
				print_usage();
				return 1;
			}else{
				password = argv[i+1];
			}
			i++;
		}else{
			fprintf(stderr, "Error: Unknown option '%s'.\n",argv[i]);
			print_usage();
			return 1;
		}
	}
	if(!id){
		id = malloc(30);
		if(!id){
			fprintf(stderr, "Error: Out of memory.\n");
			return 1;
		}
		snprintf(id, 30, "mosquitto_control_%d", getpid());
	}

	if(password && !username){
		fprintf(stderr, "Warning: Not using password since username not set.\n");
	}
	mosquitto_lib_init();
	mosq = mosquitto_new(id, NULL);
	if(!mosq){
		fprintf(stderr, "Error: Out of memory.\n");
		return 1;
	}
	if(debug){
		mosquitto_log_init(mosq, MOSQ_LOG_DEBUG | MOSQ_LOG_ERR | MOSQ_LOG_WARNING
				| MOSQ_LOG_NOTICE | MOSQ_LOG_INFO, MOSQ_LOG_STDERR);
	}
	if(username && mosquitto_username_pw_set(mosq, username, password)){
		fprintf(stderr, "Error: Problem setting username and password.\n");
		return 1;
	}

	mosquitto_connect_callback_set(mosq, my_connect_callback);
	mosquitto_disconnect_callback_set(mosq, my_disconnect_callback);
	mosquitto_publish_callback_set(mosq, my_publish_callback);

	if(mosquitto_connect(mosq, host, port, keepalive, true)){
		fprintf(stderr, "Unable to connect.\n");
		return 1;
	}

	while(!mosquitto_loop(mosq, -1) && connected){
		/* FIXME - need something here! */
		connected = false;
	}
	mosquitto_destroy(mosq);
	mosquitto_lib_cleanup();
	return 0;
}
