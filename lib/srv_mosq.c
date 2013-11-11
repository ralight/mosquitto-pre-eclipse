/*
Copyright (c) 2013 Roger Light <roger@atchoo.org>
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

#ifdef WITH_SRV
#  include <ares.h>
#endif

#include <arpa/nameser.h>
#include <stdio.h>
#include <string.h>

#include "logging_mosq.h"
#include "memory_mosq.h"
#include "mosquitto_internal.h"
#include "mosquitto.h"

#ifdef WITH_SRV
static void srv_callback(void *arg, int status, int timeouts, unsigned char *abuf, int alen)
{   
	struct mosquitto *mosq = arg;
	struct ares_srv_reply *reply = NULL;
	if(status == ARES_SUCCESS){
		status = ares_parse_srv_reply(abuf, alen, &reply);
		if(status == ARES_SUCCESS){
			// FIXME - choose which answer to use based on rfc2782 page 3. */
			mosquitto_connect(mosq, reply->host, reply->port, mosq->keepalive);
		}
	}else{
		_mosquitto_log_printf(mosq, MOSQ_LOG_ERR, "Error: SRV lookup failed (%d).", status);
		exit(1);
	}
}
#endif

int mosquitto_connect_srv(struct mosquitto *mosq, const char *host, int keepalive, const char *bind_address)
{
#ifdef WITH_SRV
	char *h;
	int rc;
	if(!mosq) return MOSQ_ERR_INVAL;

	rc = ares_init(&mosq->achan);
	if(rc != ARES_SUCCESS){
		return MOSQ_ERR_UNKNOWN;
	}

	if(!host){
		// get local domain
	}else{
		h = _mosquitto_malloc(strlen(host) + strlen("_mqtt._tcp.") + 1);
		if(!h) return MOSQ_ERR_NOMEM;
		sprintf(h, "_mqtt._tcp.%s", host);
		ares_search(mosq->achan, h, ns_c_in, ns_t_srv, srv_callback, mosq);
		_mosquitto_free(h);
	}

	pthread_mutex_lock(&mosq->state_mutex);
	mosq->state = mosq_cs_connect_srv;
	pthread_mutex_unlock(&mosq->state_mutex);

	mosq->keepalive = keepalive;

	return MOSQ_ERR_SUCCESS;

#else
	return MOSQ_ERR_NOT_SUPPORTED;
#endif
}


