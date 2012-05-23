/*
Copyright (c) 2010, Roger Light <roger@atchoo.org>
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

#include <cstdlib>
#include <mosquitto.h>
#include <mosquittopp.h>

namespace mosqpp {

static void on_connect_wrapper(struct mosquitto *mosq, void *obj, int rc)
{
	class mosquittopp *m = (class mosquittopp *)obj;
	m->on_connect(rc);
}

static void on_disconnect_wrapper(struct mosquitto *mosq, void *obj, int rc)
{
	class mosquittopp *m = (class mosquittopp *)obj;
	m->on_disconnect(rc);
}

static void on_publish_wrapper(struct mosquitto *mosq, void *obj, int mid)
{
	class mosquittopp *m = (class mosquittopp *)obj;
	m->on_publish(mid);
}

static void on_message_wrapper(struct mosquitto *mosq, void *obj, const struct mosquitto_message *message)
{
	class mosquittopp *m = (class mosquittopp *)obj;
	m->on_message(message);
}

static void on_subscribe_wrapper(struct mosquitto *mosq, void *obj, int mid, int qos_count, const int *granted_qos)
{
	class mosquittopp *m = (class mosquittopp *)obj;
	m->on_subscribe(mid, qos_count, granted_qos);
}

static void on_unsubscribe_wrapper(struct mosquitto *mosq, void *obj, int mid)
{
	class mosquittopp *m = (class mosquittopp *)obj;
	m->on_unsubscribe(mid);
}


static void on_log_wrapper(struct mosquitto *mosq, void *obj, int level, const char *str)
{
	class mosquittopp *m = (class mosquittopp *)obj;
	m->on_log(level, str);
}

void lib_version(int *major, int *minor, int *revision)
{
	if(major) *major = LIBMOSQUITTO_MAJOR;
	if(minor) *minor = LIBMOSQUITTO_MINOR;
	if(revision) *revision = LIBMOSQUITTO_REVISION;
}

int lib_init()
{
	return mosquitto_lib_init();
}

int lib_cleanup()
{
	return mosquitto_lib_cleanup();
}

const char* strerror(int mosq_errno)
{
	return mosquitto_strerror(mosq_errno);
}

const char* connack_string(int connack_code)
{
	return mosquitto_connack_string(connack_code);
}

mosquittopp::mosquittopp(const char *id, bool clean_session)
{
	m_mosq = mosquitto_new(id, clean_session, this);
	mosquitto_connect_callback_set(m_mosq, on_connect_wrapper);
	mosquitto_disconnect_callback_set(m_mosq, on_disconnect_wrapper);
	mosquitto_publish_callback_set(m_mosq, on_publish_wrapper);
	mosquitto_message_callback_set(m_mosq, on_message_wrapper);
	mosquitto_subscribe_callback_set(m_mosq, on_subscribe_wrapper);
	mosquitto_unsubscribe_callback_set(m_mosq, on_unsubscribe_wrapper);
	mosquitto_log_callback_set(m_mosq, on_log_wrapper);
}

mosquittopp::~mosquittopp()
{
	mosquitto_destroy(m_mosq);
}

int mosquittopp::connect(const char *host, int port, int keepalive)
{
	return mosquitto_connect(m_mosq, host, port, keepalive);
}

int mosquittopp::connect_async(const char *host, int port, int keepalive)
{
	return mosquitto_connect_async(m_mosq, host, port, keepalive);
}

int mosquittopp::reconnect()
{
	return mosquitto_reconnect(m_mosq);
}

int mosquittopp::disconnect()
{
	return mosquitto_disconnect(m_mosq);
}

int mosquittopp::socket()
{
	return mosquitto_socket(m_mosq);
}

int mosquittopp::will_set(const char *topic, uint32_t payloadlen, const uint8_t *payload, int qos, bool retain)
{
	return mosquitto_will_set(m_mosq, topic, payloadlen, payload, qos, retain);
}

int mosquittopp::will_clear()
{
	return mosquitto_will_clear(m_mosq);
}

int mosquittopp::username_pw_set(const char *username, const char *password)
{
	return mosquitto_username_pw_set(m_mosq, username, password);
}

int mosquittopp::publish(int *mid, const char *topic, uint32_t payloadlen, const uint8_t *payload, int qos, bool retain)
{
	return mosquitto_publish(m_mosq, mid, topic, payloadlen, payload, qos, retain);
}

void mosquittopp::message_retry_set(unsigned int message_retry)
{
	mosquitto_message_retry_set(m_mosq, message_retry);
}

int mosquittopp::subscribe(int *mid, const char *sub, int qos)
{
	return mosquitto_subscribe(m_mosq, mid, sub, qos);
}

int mosquittopp::unsubscribe(int *mid, const char *sub)
{
	return mosquitto_unsubscribe(m_mosq, mid, sub);
}

int mosquittopp::loop(int timeout)
{
	return mosquitto_loop(m_mosq, timeout);
}

int mosquittopp::loop_misc()
{
	return mosquitto_loop_misc(m_mosq);
}

int mosquittopp::loop_read()
{
	return mosquitto_loop_read(m_mosq);
}

int mosquittopp::loop_write()
{
	return mosquitto_loop_write(m_mosq);
}

int mosquittopp::loop_start()
{
	return mosquitto_loop_start(m_mosq);
}

int mosquittopp::loop_stop(bool force)
{
	return mosquitto_loop_stop(m_mosq, force);
}

bool mosquittopp::want_write()
{
	return mosquitto_want_write(m_mosq);
}

void mosquittopp::user_data_set(void *obj)
{
	mosquitto_user_data_set(m_mosq, obj);
}

}
