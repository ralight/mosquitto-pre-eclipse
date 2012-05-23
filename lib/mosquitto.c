/*
Copyright (c) 2010-2012 Roger Light <roger@atchoo.org>
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

#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#ifndef WIN32
#include <sys/select.h>
#include <sys/time.h>
#include <unistd.h>
#else
#include <winsock2.h>
#include <windows.h>
typedef int ssize_t;
#endif

#include <mosquitto.h>
#include <mosquitto_internal.h>
#include <logging_mosq.h>
#include <messages_mosq.h>
#include <memory_mosq.h>
#include <mqtt3_protocol.h>
#include <net_mosq.h>
#include <read_handle.h>
#include <send_mosq.h>
#include <util_mosq.h>
#include <will_mosq.h>

#if !defined(WIN32) && defined(__SYMBIAN32__)
#define HAVE_PSELECT
#endif

void mosquitto_lib_version(int *major, int *minor, int *revision)
{
	if(major) *major = LIBMOSQUITTO_MAJOR;
	if(minor) *minor = LIBMOSQUITTO_MINOR;
	if(revision) *revision = LIBMOSQUITTO_REVISION;
}

int mosquitto_lib_init(void)
{
#ifdef WIN32
	srand(GetTickCount());
#else
	struct timeval tv;

	gettimeofday(&tv, NULL);
	srand(tv.tv_sec*1000 + tv.tv_usec/1000);
#endif

	_mosquitto_net_init();

	return MOSQ_ERR_SUCCESS;
}

int mosquitto_lib_cleanup(void)
{
	_mosquitto_net_cleanup();

	return MOSQ_ERR_SUCCESS;
}

struct mosquitto *mosquitto_new(const char *id, bool clean_session, void *obj)
{
	struct mosquitto *mosq = NULL;
	int i;

	if(clean_session == false && id == NULL){
		errno = EINVAL;
		return NULL;
	}

	mosq = (struct mosquitto *)_mosquitto_calloc(1, sizeof(struct mosquitto));
	if(mosq){
		if(obj){
			mosq->obj = obj;
		}else{
			mosq->obj = mosq;
		}
		mosq->sock = INVALID_SOCKET;
		mosq->keepalive = 60;
		mosq->message_retry = 20;
		mosq->last_retry_check = 0;
		mosq->clean_session = clean_session;
		if(id){
			if(strlen(id) == 0){
				_mosquitto_free(mosq);
				errno = EINVAL;
				return NULL;
			}
			mosq->id = _mosquitto_strdup(id);
		}else{
			mosq->id = (char *)_mosquitto_calloc(24, sizeof(char));
			if(!mosq->id){
				_mosquitto_free(mosq);
				errno = ENOMEM;
				return NULL;
			}
			mosq->id[0] = 'm';
			mosq->id[1] = 'o';
			mosq->id[2] = 's';
			mosq->id[3] = 'q';
			mosq->id[4] = '/';

			for(i=5; i<23; i++){
				mosq->id[i] = (rand()%73)+48;
			}
		}
		mosq->username = NULL;
		mosq->password = NULL;
		mosq->in_packet.payload = NULL;
		_mosquitto_packet_cleanup(&mosq->in_packet);
		mosq->out_packet = NULL;
		mosq->current_out_packet = NULL;
		mosq->last_msg_in = time(NULL);
		mosq->last_msg_out = time(NULL);
		mosq->ping_t = 0;
		mosq->last_mid = 0;
		mosq->state = mosq_cs_new;
		mosq->messages = NULL;
		mosq->will = NULL;
		mosq->on_connect = NULL;
		mosq->on_publish = NULL;
		mosq->on_message = NULL;
		mosq->on_subscribe = NULL;
		mosq->on_unsubscribe = NULL;
		mosq->host = NULL;
		mosq->port = 1883;
		mosq->in_callback = false;
#ifdef WITH_SSL
		mosq->ssl = NULL;
#endif
		pthread_mutex_init(&mosq->callback_mutex, NULL);
		pthread_mutex_init(&mosq->log_callback_mutex, NULL);
		pthread_mutex_init(&mosq->state_mutex, NULL);
		pthread_mutex_init(&mosq->out_packet_mutex, NULL);
		pthread_mutex_init(&mosq->current_out_packet_mutex, NULL);
		pthread_mutex_init(&mosq->msgtime_mutex, NULL);
	}else{
		errno = ENOMEM;
	}
	return mosq;
}

int mosquitto_will_set(struct mosquitto *mosq, const char *topic, uint32_t payloadlen, const uint8_t *payload, int qos, bool retain)
{
	if(!mosq) return MOSQ_ERR_INVAL;
	return _mosquitto_will_set(mosq, topic, payloadlen, payload, qos, retain);
}

int mosquitto_will_clear(struct mosquitto *mosq)
{
	if(!mosq) return MOSQ_ERR_INVAL;
	return _mosquitto_will_clear(mosq);
}

int mosquitto_username_pw_set(struct mosquitto *mosq, const char *username, const char *password)
{
	if(!mosq) return MOSQ_ERR_INVAL;

	if(username){
		mosq->username = _mosquitto_strdup(username);
		if(!mosq->username) return MOSQ_ERR_NOMEM;
		if(mosq->password){
			_mosquitto_free(mosq->password);
			mosq->password = NULL;
		}
		if(password){
			mosq->password = _mosquitto_strdup(password);
			if(!mosq->password){
				_mosquitto_free(mosq->username);
				mosq->username = NULL;
				return MOSQ_ERR_NOMEM;
			}
		}
	}else{
		if(mosq->username){
			_mosquitto_free(mosq->username);
			mosq->username = NULL;
		}
		if(mosq->password){
			_mosquitto_free(mosq->password);
			mosq->password = NULL;
		}
	}
	return MOSQ_ERR_SUCCESS;
}


void mosquitto_destroy(struct mosquitto *mosq)
{
	if(mosq->id) _mosquitto_free(mosq->id);
	_mosquitto_message_cleanup_all(mosq);
	if(mosq->will){
		if(mosq->will->topic) _mosquitto_free(mosq->will->topic);
		if(mosq->will->payload) _mosquitto_free(mosq->will->payload);
		_mosquitto_free(mosq->will);
	}
	if(mosq->host){
		_mosquitto_free(mosq->host);
	}
#ifdef WITH_SSL
	if(mosq->ssl){
		if(mosq->ssl->ssl){
			SSL_free(mosq->ssl->ssl);
		}
		if(mosq->ssl->ssl_ctx){
			SSL_CTX_free(mosq->ssl->ssl_ctx);
		}
		_mosquitto_free(mosq->ssl);
	}
#endif
	pthread_mutex_destroy(&mosq->callback_mutex);
	pthread_mutex_destroy(&mosq->log_callback_mutex);
	pthread_mutex_destroy(&mosq->state_mutex);
	pthread_mutex_destroy(&mosq->out_packet_mutex);
	pthread_mutex_destroy(&mosq->current_out_packet_mutex);
	pthread_mutex_destroy(&mosq->msgtime_mutex);
	_mosquitto_free(mosq);
}

int mosquitto_socket(struct mosquitto *mosq)
{
	if(!mosq) return MOSQ_ERR_INVAL;
	return mosq->sock;
}

int mosquitto_connect(struct mosquitto *mosq, const char *host, int port, int keepalive)
{
	int rc;
	rc = mosquitto_connect_async(mosq, host, port, keepalive);
	if(rc) return rc;

	return mosquitto_reconnect(mosq);
}

int mosquitto_connect_async(struct mosquitto *mosq, const char *host, int port, int keepalive)
{
	if(!mosq) return MOSQ_ERR_INVAL;
	if(!host || port <= 0) return MOSQ_ERR_INVAL;

	if(mosq->host) _mosquitto_free(mosq->host);
	mosq->host = _mosquitto_strdup(host);
	if(!mosq->host) return MOSQ_ERR_NOMEM;
	mosq->port = port;

	mosq->keepalive = keepalive;
	pthread_mutex_lock(&mosq->state_mutex);
	mosq->state = mosq_cs_connect_async;
	pthread_mutex_unlock(&mosq->state_mutex);

	return MOSQ_ERR_SUCCESS;
}

int mosquitto_reconnect(struct mosquitto *mosq)
{
	int rc;
	if(!mosq) return MOSQ_ERR_INVAL;
	if(!mosq->host || mosq->port <= 0) return MOSQ_ERR_INVAL;

	pthread_mutex_lock(&mosq->state_mutex);
	mosq->state = mosq_cs_new;
	pthread_mutex_unlock(&mosq->state_mutex);
	rc = _mosquitto_socket_connect(mosq, mosq->host, mosq->port);
	if(rc){
		return rc;
	}

	return _mosquitto_send_connect(mosq, mosq->keepalive, mosq->clean_session);
}

int mosquitto_disconnect(struct mosquitto *mosq)
{
	if(!mosq) return MOSQ_ERR_INVAL;
	if(mosq->sock == INVALID_SOCKET) return MOSQ_ERR_NO_CONN;

	pthread_mutex_lock(&mosq->state_mutex);
	mosq->state = mosq_cs_disconnecting;
	pthread_mutex_unlock(&mosq->state_mutex);

	return _mosquitto_send_disconnect(mosq);
}

int mosquitto_publish(struct mosquitto *mosq, uint16_t *mid, const char *topic, uint32_t payloadlen, const uint8_t *payload, int qos, bool retain)
{
	struct mosquitto_message_all *message;
	uint16_t local_mid;

	if(!mosq || !topic || qos<0 || qos>2) return MOSQ_ERR_INVAL;
	if(strlen(topic) == 0) return MOSQ_ERR_INVAL;
	if(payloadlen > 268435455) return MOSQ_ERR_PAYLOAD_SIZE;

	if(_mosquitto_topic_wildcard_len_check(topic) != MOSQ_ERR_SUCCESS){
		return MOSQ_ERR_INVAL;
	}

	local_mid = _mosquitto_mid_generate(mosq);
	if(mid){
		*mid = local_mid;
	}

	if(qos == 0){
		return _mosquitto_send_publish(mosq, local_mid, topic, payloadlen, payload, qos, retain, false);
	}else{
		message = _mosquitto_calloc(1, sizeof(struct mosquitto_message_all));
		if(!message) return MOSQ_ERR_NOMEM;

		message->next = NULL;
		message->timestamp = time(NULL);
		message->direction = mosq_md_out;
		if(qos == 1){
			message->state = mosq_ms_wait_puback;
		}else if(qos == 2){
			message->state = mosq_ms_wait_pubrec;
		}
		message->msg.mid = local_mid;
		message->msg.topic = _mosquitto_strdup(topic);
		if(!message->msg.topic){
			_mosquitto_message_cleanup(&message);
			return MOSQ_ERR_NOMEM;
		}
		if(payloadlen){
			message->msg.payloadlen = payloadlen;
			message->msg.payload = _mosquitto_malloc(payloadlen*sizeof(uint8_t));
			if(!message->msg.payload){
				_mosquitto_message_cleanup(&message);
				return MOSQ_ERR_NOMEM;
			}
			memcpy(message->msg.payload, payload, payloadlen*sizeof(uint8_t));
		}else{
			message->msg.payloadlen = 0;
			message->msg.payload = NULL;
		}
		message->msg.qos = qos;
		message->msg.retain = retain;
		message->dup = false;

		_mosquitto_message_queue(mosq, message);
		return _mosquitto_send_publish(mosq, message->msg.mid, message->msg.topic, message->msg.payloadlen, message->msg.payload, message->msg.qos, message->msg.retain, message->dup);
	}
}

int mosquitto_subscribe(struct mosquitto *mosq, uint16_t *mid, const char *sub, int qos)
{
	if(!mosq) return MOSQ_ERR_INVAL;
	if(mosq->sock == INVALID_SOCKET) return MOSQ_ERR_NO_CONN;

	return _mosquitto_send_subscribe(mosq, mid, false, sub, qos);
}

int mosquitto_unsubscribe(struct mosquitto *mosq, uint16_t *mid, const char *sub)
{
	if(!mosq) return MOSQ_ERR_INVAL;
	if(mosq->sock == INVALID_SOCKET) return MOSQ_ERR_NO_CONN;

	return _mosquitto_send_unsubscribe(mosq, mid, false, sub);
}

#if 0
int mosquitto_ssl_set(struct mosquitto *mosq, const char *pemfile, const char *password)
{
#ifdef WITH_SSL
	if(!mosq || mosq->ssl) return MOSQ_ERR_INVAL; //FIXME

	mosq->ssl = _mosquitto_malloc(sizeof(struct _mosquitto_ssl));
	if(!mosq->ssl) return MOSQ_ERR_NOMEM;

	mosq->ssl->ssl_ctx = SSL_CTX_new(TLSv1_method());
	if(!mosq->ssl->ssl_ctx) return MOSQ_ERR_SSL;

	mosq->ssl->ssl = SSL_new(mosq->ssl->ssl_ctx);

	return MOSQ_ERR_SUCCESS;
#else
	return MOSQ_ERR_NOT_SUPPORTED;
#endif
}
#endif

int mosquitto_loop(struct mosquitto *mosq, int timeout)
{
#ifdef HAVE_PSELECT
	struct timespec local_timeout;
#else
	struct timeval local_timeout;
#endif
	fd_set readfds, writefds;
	int fdcount;
	int rc;

	if(!mosq) return MOSQ_ERR_INVAL;
	if(mosq->sock == INVALID_SOCKET) return MOSQ_ERR_NO_CONN;

	FD_ZERO(&readfds);
	FD_SET(mosq->sock, &readfds);
	FD_ZERO(&writefds);
	pthread_mutex_lock(&mosq->out_packet_mutex);
	if(mosq->out_packet || mosq->current_out_packet){
		FD_SET(mosq->sock, &writefds);
#ifdef WITH_SSL
	}else if(mosq->ssl && mosq->ssl->want_write){
		FD_SET(mosq->sock, &writefds);
#endif
	}
	pthread_mutex_unlock(&mosq->out_packet_mutex);
	if(timeout >= 0){
		local_timeout.tv_sec = timeout/1000;
#ifdef HAVE_PSELECT
		local_timeout.tv_nsec = (timeout-local_timeout.tv_sec*1000)*1e6;
#else
		local_timeout.tv_usec = (timeout-local_timeout.tv_sec*1000)*1000;
#endif
	}else{
		local_timeout.tv_sec = 1;
#ifdef HAVE_PSELECT
		local_timeout.tv_nsec = 0;
#else
		local_timeout.tv_usec = 0;
#endif
	}

#ifdef HAVE_PSELECT
	fdcount = pselect(mosq->sock+1, &readfds, &writefds, NULL, &local_timeout, NULL);
#else
	fdcount = select(mosq->sock+1, &readfds, &writefds, NULL, &local_timeout);
#endif
	if(fdcount == -1){
#ifdef WIN32
		errno = WSAGetLastError();
#endif
		return MOSQ_ERR_ERRNO;
	}else{
		if(FD_ISSET(mosq->sock, &readfds)){
			rc = mosquitto_loop_read(mosq);
			if(rc){
				_mosquitto_socket_close(mosq);
				pthread_mutex_lock(&mosq->state_mutex);
				if(mosq->state == mosq_cs_disconnecting){
					rc = MOSQ_ERR_SUCCESS;
				}
				pthread_mutex_unlock(&mosq->state_mutex);
				pthread_mutex_lock(&mosq->callback_mutex);
				if(mosq->on_disconnect){
					mosq->in_callback = true;
					mosq->on_disconnect(mosq, mosq->obj, rc);
					mosq->in_callback = false;
				}
				pthread_mutex_unlock(&mosq->callback_mutex);
				return rc;
			}
		}
		if(FD_ISSET(mosq->sock, &writefds)){
			rc = mosquitto_loop_write(mosq);
			if(rc){
				_mosquitto_socket_close(mosq);
				pthread_mutex_lock(&mosq->state_mutex);
				if(mosq->state == mosq_cs_disconnecting){
					rc = MOSQ_ERR_SUCCESS;
				}
				pthread_mutex_unlock(&mosq->state_mutex);
				pthread_mutex_lock(&mosq->callback_mutex);
				if(mosq->on_disconnect){
					mosq->in_callback = true;
					mosq->on_disconnect(mosq, mosq->obj, rc);
					mosq->in_callback = false;
				}
				pthread_mutex_unlock(&mosq->callback_mutex);
				return rc;
			}
		}
	}
	return mosquitto_loop_misc(mosq);
}

int mosquitto_loop_misc(struct mosquitto *mosq)
{
	time_t now = time(NULL);

	if(!mosq) return MOSQ_ERR_INVAL;
	if(mosq->sock == INVALID_SOCKET) return MOSQ_ERR_NO_CONN;

	_mosquitto_check_keepalive(mosq);
	if(mosq->last_retry_check+1 < now){
		_mosquitto_message_retry_check(mosq);
		mosq->last_retry_check = now;
	}
	if(mosq->ping_t && now - mosq->ping_t >= mosq->keepalive){
		/* mosq->ping_t != 0 means we are waiting for a pingresp.
		 * This hasn't happened in the keepalive time so we should disconnect.
		 */
		_mosquitto_socket_close(mosq);
		return MOSQ_ERR_CONN_LOST;
	}
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_loop_read(struct mosquitto *mosq)
{
	return _mosquitto_packet_read(mosq);
}

int mosquitto_loop_write(struct mosquitto *mosq)
{
	return _mosquitto_packet_write(mosq);
}

bool mosquitto_want_write(struct mosquitto *mosq)
{
	if(mosq->out_packet){
		return true;
	}else{
		return false;
	}
}

void mosquitto_connect_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int))
{
	pthread_mutex_lock(&mosq->callback_mutex);
	mosq->on_connect = on_connect;
	pthread_mutex_unlock(&mosq->callback_mutex);
}

void mosquitto_disconnect_callback_set(struct mosquitto *mosq, void (*on_disconnect)(struct mosquitto *, void *, int))
{
	pthread_mutex_lock(&mosq->callback_mutex);
	mosq->on_disconnect = on_disconnect;
	pthread_mutex_unlock(&mosq->callback_mutex);
}

void mosquitto_publish_callback_set(struct mosquitto *mosq, void (*on_publish)(struct mosquitto *, void *, uint16_t))
{
	pthread_mutex_lock(&mosq->callback_mutex);
	mosq->on_publish = on_publish;
	pthread_mutex_unlock(&mosq->callback_mutex);
}

void mosquitto_message_callback_set(struct mosquitto *mosq, void (*on_message)(struct mosquitto *, void *, const struct mosquitto_message *))
{
	pthread_mutex_lock(&mosq->callback_mutex);
	mosq->on_message = on_message;
	pthread_mutex_unlock(&mosq->callback_mutex);
}

void mosquitto_subscribe_callback_set(struct mosquitto *mosq, void (*on_subscribe)(struct mosquitto *, void *, uint16_t, int, const uint8_t *))
{
	pthread_mutex_lock(&mosq->callback_mutex);
	mosq->on_subscribe = on_subscribe;
	pthread_mutex_unlock(&mosq->callback_mutex);
}

void mosquitto_unsubscribe_callback_set(struct mosquitto *mosq, void (*on_unsubscribe)(struct mosquitto *, void *, uint16_t))
{
	pthread_mutex_lock(&mosq->callback_mutex);
	mosq->on_unsubscribe = on_unsubscribe;
	pthread_mutex_unlock(&mosq->callback_mutex);
}

void mosquitto_log_callback_set(struct mosquitto *mosq, void (*on_log)(struct mosquitto *, void *, int, const char *))
{
	pthread_mutex_lock(&mosq->log_callback_mutex);
	mosq->on_log = on_log;
	pthread_mutex_unlock(&mosq->log_callback_mutex);
}

void mosquitto_user_data_set(struct mosquitto *mosq, void *obj)
{
	if(mosq){
		mosq->obj = obj;
	}
}

const char *mosquitto_strerror(int mosq_errno)
{
	switch(mosq_errno){
		case MOSQ_ERR_SUCCESS:
			return "No error.";
		case MOSQ_ERR_NOMEM:
			return "Out of memory.";
		case MOSQ_ERR_PROTOCOL:
			return "A network protocol error occurred when communicating with the broker.";
		case MOSQ_ERR_INVAL:
			return "Invalid function arguments provided.";
		case MOSQ_ERR_NO_CONN:
			return "The client is not currently connected.";
		case MOSQ_ERR_CONN_REFUSED:
			return "The connection was refused.";
		case MOSQ_ERR_NOT_FOUND:
			return "Message not found (internal error).";
		case MOSQ_ERR_CONN_LOST:
			return "The connection was lost.";
		case MOSQ_ERR_SSL:
			return "An SSL error occurred.";
		case MOSQ_ERR_PAYLOAD_SIZE:
			return "Payload too large.";
		case MOSQ_ERR_NOT_SUPPORTED:
			return "This feature is not supported.";
		case MOSQ_ERR_AUTH:
			return "Authorisation failed.";
		case MOSQ_ERR_ACL_DENIED:
			return "Access denied by ACL.";
		case MOSQ_ERR_UNKNOWN:
			return "Unknown error.";
		case MOSQ_ERR_ERRNO:
			return "Error defined by errno.";
		default:
			return "Unknown error.";
	}
}

const char *mosquitto_connack_string(int connack_code)
{
	switch(connack_code){
		case 0:
			return "Connection Accepted.";
		case 1:
			return "Connection Refused: unacceptable protocol version.";
		case 2:
			return "Connection Refused: identifier rejected.";
		case 3:
			return "Connection Refused: broker unavailable.";
		case 4:
			return "Connection Refused: bad user name or password.";
		case 5:
			return "Connection Refused: not authorised.";
		default:
			return "Connection Refused: unknown reason.";
	}
}

