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

#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/select.h>
#include <unistd.h>

#include <config.h>
#include <mqtt3.h>

int mqtt3_handle_connect(mqtt3_context *context)
{
	char *protocol_name;
	uint8_t protocol_version;
	uint8_t connect_flags;
	char *client_id;
	char *will_topic = NULL, *will_message = NULL;
	uint8_t will, will_retain, will_qos, clean_start;
	
	/* Don't accept multiple CONNECT commands. */
	if(context->connected) return 1;

	if(mqtt3_read_string(context, &protocol_name)) return 1;
	if(!protocol_name){
		mqtt3_socket_close(context);
		return 3;
	}
	if(strcmp(protocol_name, PROTOCOL_NAME)){
		mqtt3_log_printf(MQTT3_LOG_INFO, "Invalid protocol \"%s\" in CONNECT from %s.",
				protocol_name, context->address);
		mqtt3_free(protocol_name);
		mqtt3_socket_close(context);
		return 1;
	}
	if(mqtt3_read_byte(context, &protocol_version)) return 1;
	if(protocol_version != PROTOCOL_VERSION){
		mqtt3_log_printf(MQTT3_LOG_INFO, "Invalid protocol version %d in CONNECT from %s.",
				protocol_version, context->address);
		mqtt3_free(protocol_name);
		mqtt3_raw_connack(context, 1);
		mqtt3_socket_close(context);
		return 1;
	}

	mqtt3_free(protocol_name);

	if(mqtt3_read_byte(context, &connect_flags)) return 1;
	clean_start = connect_flags & 0x02;
	will = connect_flags & 0x04;
	will_qos = (connect_flags & 0x18) >> 2;
	will_retain = connect_flags & 0x20;

	if(mqtt3_read_uint16(context, &(context->keepalive))) return 1;

	if(mqtt3_read_string(context, &client_id)) return 1;
	if(connect_flags & 0x04){
		if(mqtt3_read_string(context, &will_topic)) return 1;
		if(mqtt3_read_string(context, &will_message)) return 1;
	}

	mqtt3_log_printf(MQTT3_LOG_DEBUG, "Received CONNECT from %s as %s", context->address, client_id);
	context->id = client_id;
	context->clean_start = clean_start;

	mqtt3_db_client_insert(context, will, will_retain, will_qos, will_topic, will_message);

	if(will_topic) mqtt3_free(will_topic);
	if(will_message) mqtt3_free(will_message);

	context->connected = true;
	return mqtt3_raw_connack(context, 0);
}

int mqtt3_handle_disconnect(mqtt3_context *context)
{
	mqtt3_log_printf(MQTT3_LOG_DEBUG, "Received DISCONNECT from %s", context->id);
	context->disconnecting = true;
	return mqtt3_socket_close(context);
}


int mqtt3_handle_subscribe(mqtt3_context *context)
{
	int rc = 0;
	uint16_t mid;
	char *sub;
	uint8_t qos;
	uint8_t *payload = NULL;
	uint32_t payloadlen = 0;

	mqtt3_log_printf(MQTT3_LOG_DEBUG, "Received SUBSCRIBE from %s", context->id);
	/* FIXME - plenty of potential for memory leaks here */
	if(!context) return 1;

	if(mqtt3_read_uint16(context, &mid)) return 1;

	while(context->in_packet.pos < context->in_packet.remaining_length){
		sub = NULL;
		if(mqtt3_read_string(context, &sub)){
			if(sub) mqtt3_free(sub);
			return 1;
		}

		if(mqtt3_read_byte(context, &qos)) return 1;
		if(sub){
			if(mqtt3_fix_sub_topic(&sub)) return 1;
			if(!strlen(sub)){
				mqtt3_log_printf(MQTT3_LOG_INFO, "Empty subscription string from %s, disconnecting.",
					context->address);
				return 1;
			}
			mqtt3_log_printf(MQTT3_LOG_DEBUG, "\t%s (QoS %d)", sub, qos);
			mqtt3_db_sub_insert(context->id, sub, qos);
	
			if(mqtt3_db_retain_queue(context, sub, qos)) rc = 1;
			mqtt3_free(sub);
		}

		payload = mqtt3_realloc(payload, payloadlen + 1);
		payload[payloadlen] = qos;
		payloadlen++;
	}

	if(mqtt3_raw_suback(context, mid, payloadlen, payload)) rc = 1;
	mqtt3_free(payload);
	
	return rc;
}

int mqtt3_handle_unsubscribe(mqtt3_context *context)
{
	uint16_t mid;
	char *sub;

	mqtt3_log_printf(MQTT3_LOG_DEBUG, "Received UNSUBSCRIBE from %s", context->id);
	if(!context) return 1;

	if(mqtt3_read_uint16(context, &mid)) return 1;

	while(context->in_packet.pos < context->in_packet.remaining_length){
		sub = NULL;
		if(mqtt3_read_string(context, &sub)){
			if(sub) mqtt3_free(sub);
			return 1;
		}

		if(sub){
			mqtt3_log_printf(MQTT3_LOG_DEBUG, "\t%s", sub);
			mqtt3_db_sub_delete(context->id, sub);
			mqtt3_free(sub);
		}
	}

	if(mqtt3_send_command_with_mid(context, UNSUBACK, mid)) return 1;

	return 0;
}

