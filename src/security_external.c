/*
Copyright (c) 2011,2012 Roger Light <roger@atchoo.org>
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

#ifndef CMAKE
#include <config.h>
#endif

#include <stdio.h>
#include <string.h>

#include <mosquitto_broker.h>
#include <memory_mosq.h>

#ifdef WITH_EXTERNAL_SECURITY_CHECKS

int mosquitto_acl_init(struct _mosquitto_db *db)
{
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_acl_check(struct _mosquitto_db *db, struct mosquitto *context, const char *topic, int access)
{
	return MOSQ_ERR_ACL_DENIED;
}

void mosquitto_acl_cleanup(struct _mosquitto_db *db)
{
}

/*
 * Function: mosquitto_security_apply
 *
 * This function is called after the broker receives a signal to reload its
 * configuration. <mosquitto_security_cleanup> and <mosquitto_security_init>
 * will have already been called when <mosquitto_security_apply> is called, so
 * the acl and unpwd cleanup and init functions will have also been called.
 *
 * You should use this function to apply any settings that have been changed. The built in checks do the following:
 *
 * - Disconnect anonymous users if appropriate
 * - Disconnect users with invalid passwords
 * - Reapply ACLs
 *
 * The return value isn't currently checked.
 */
int mosquitto_security_apply(struct _mosquitto_db *db)
{
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_unpwd_init(struct _mosquitto_db *db)
{
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_unpwd_check(struct _mosquitto_db *db, const char *username, const char *password)
{
	return MOSQ_ERR_AUTH;
}

int mosquitto_unpwd_cleanup(struct _mosquitto_db *db)
{
	return MOSQ_ERR_SUCCESS;
}

#endif
