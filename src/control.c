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

#include <config.h>
#ifdef WITH_CONTROL

#include <stdio.h>
#include <string.h>

#include <memory_mosq.h>
#include <mqtt3.h>

static int _control_user_add(struct _mosquitto_db *db, mqtt3_context *context, struct mosquitto_msg_store *stored, const char *topic)
{
	int rc = MOSQ_ERR_SUCCESS;
	char *username, *password;
	char *payload;

	payload = _mosquitto_calloc(stored->msg.payloadlen+1, sizeof(char));
	if(!payload) return MOSQ_ERR_NOMEM;
	memcpy(payload, stored->msg.payload, stored->msg.payloadlen);
	username = strtok(payload, ":");
	if(username){
		password = strtok(NULL, ":");
		rc = mqtt3_user_add(db, username, password);
	}
	_mosquitto_free(payload);

	return rc;
}

static int _control_user_list(struct _mosquitto_db *db, mqtt3_context *context, const char *topic)
{
	struct _mosquitto_unpwd *unpwd = NULL;
	int rc = 0;
	char *buf;
	int len;

	unpwd = db->unpwd;
	while(!rc && unpwd){
		if(unpwd->username){
			len = strlen(unpwd->username) + 11;
			buf = _mosquitto_malloc(len);
			if(!buf) return MOSQ_ERR_NOMEM;
			if(unpwd->password){
				snprintf(buf, len, "%s:XXXXXXXXXX", unpwd->username);
			}else{
				snprintf(buf, len, "%s", unpwd->username);
			}
			rc = mqtt3_db_messages_easy_queue(db, NULL, topic, 2, strlen(buf), (uint8_t *)buf, 0);
			_mosquitto_free(buf);
		}
		unpwd = unpwd->next;
	}
	/* Send a zero length message as an end-of-data signifier. */
	rc = mqtt3_db_messages_easy_queue(db, NULL, topic, 2, 0, NULL, 0);
	return rc;
}

int mosquitto_control_process(struct _mosquitto_db *db, const char *source_id, const char *topic, struct mosquitto_msg_store *stored)
{
	int rc = MOSQ_ERR_SUCCESS;
	mqtt3_context *context;
	int len;
	char *result_topic;

	if(!source_id) return MOSQ_ERR_SUCCESS;

	context = mqtt3_context_find(db, source_id);
	if(!context) return MOSQ_ERR_UNKNOWN;

	len = strlen(context->core.id) + strlen("$SYS/control/result/");
	result_topic = _mosquitto_calloc(len + 1, sizeof(char));
	if(!result_topic) return MOSQ_ERR_NOMEM;
	snprintf(result_topic, len, "$SYS/control/result/%s", context->core.id);

	if(!strcmp(topic, "$SYS/control/user/add")){
		if(stored->msg.payloadlen && stored->msg.payload){
			rc = _control_user_add(db, context, stored, result_topic);
		}else{
			/* FIXME - send an error message back. */
		}
	}else if(!strcmp(topic, "$SYS/control/user/list")){
		rc = _control_user_list(db, context, result_topic);
	}

	_mosquitto_free(result_topic);
	return rc;
}

#endif
