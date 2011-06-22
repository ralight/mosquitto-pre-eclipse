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
#ifndef _THREAD_MOSQ_H_
#define _THREAD_MOSQ_H_

#ifdef WITH_THREADING
#	ifdef WIN32
#		include <windows.h>
		typedef CRITICAL_SECTION mosquitto_mutex_t;
#		define MOSQUITTO_MUTEX_INIT(a) InitializeCriticalSection(a)
#		define MOSQUITTO_MUTEX_DESTROY(a) DeleteCriticalSection(a)
#		define MOSQUITTO_MUTEX_LOCK(a) EnterCriticalSection(a)
#		define MOSQUITTO_MUTEX_UNLOCK(a) LeaveCriticalSection(a)
#	else
#		include <pthread.h>
		typedef pthread_mutex_t mosquitto_mutex_t;
#		define MOSQUITTO_MUTEX_INIT(a) pthread_mutex_init(a, NULL)
#		define MOSQUITTO_MUTEX_DESTROY(a) pthread_mutex_destroy(a)
#		define MOSQUITTO_MUTEX_LOCK(a) pthread_mutex_lock(a)
#		define MOSQUITTO_MUTEX_UNLOCK(a) pthread_mutex_unlock(a)
#	endif
#else
#	define MOSQUITTO_MUTEX_INIT(a)
#	define MOSQUITTO_MUTEX_DESTROY(a)
#	define MOSQUITTO_MUTEX_LOCK(a)
#	define MOSQUITTO_MUTEX_UNLOCK(a)
#endif


#endif
