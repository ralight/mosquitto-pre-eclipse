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

/*
 * Function: mosquitto_acl_init
 *
 * This function is called when the broker starts up. It should be used to
 * initialise data structures or connect to data providers relating to access
 * control lists. This may be unnecessary in some situations, for example if a
 * SQL server is used to store both username, password and ACL information then
 * one one of <mosquitto_acl_init> and <mosquitto_unpwd_init> need be used.
 *
 * This function will also be called when the broker receives a signal to
 * reload its configuration. In this situation <mosquitto_acl_cleanup> will be
 * called followed by <mosquitto_acl_init>.
 *
 * Parameters:
 *	db - main broker data structer
 *	reload - set to true if this function is being called as part of a config
 *           reload.
 */
int mosquitto_acl_init(struct _mosquitto_db *db, bool reload)
{
	return MOSQ_ERR_SUCCESS;
}

/*
 * Function: mosquitto_acl_check
 *
 * This function is called when it is necessary to verify whether a client has
 * access to a given topic with a given access.
 *
 * The client information can be found in the context variable, with the
 * relevant members being:
 * - context->id (the client id, unique per client)
 * - context->username (the client username or NULL if none was given)
 * - context->password (the client password, or NULL if none was given)
 *
 * Your function should handle the possibility of one or both of username or
 * password being NULL. 
 * 
 * The topic that the client is attempting to access is stored in the topic
 * variable and the type of access in access. Access will be one of
 * MOSQ_ACL_READ and MOSQ_ACL_WRITE, where READ is for messages being sent to
 * the client and WRITE is for messages from the client.
 *
 * Returns:
 *	MOSQ_ERR_SUCCESS - if the client was granted access.
 *	MOSQ_ERR_ACL_DENIED - if the client was denied access.
 *	other - see lib/mosquitto.h for appropriate values.
 */
int mosquitto_acl_check(struct _mosquitto_db *db, struct mosquitto *context, const char *topic, int access)
{
	return MOSQ_ERR_ACL_DENIED;
}

/*
 * Function: mosquitto_acl_cleanup
 *
 * This function is called when the broker shuts down. It should be used to
 * free data structures or disconnect from data providers relating to access
 * control lists.
 *
 * This function will also be called when the broker receives a signal to
 * reload its configuration. In this situation <mosquitto_acl_cleanup> will be
 * called followed by <mosquitto_acl_init>.
 *
 * Parameters:
 *	db - main broker data structer
 *	reload - set to true if this function is being called as part of a config
 *           reload.
 */
void mosquitto_acl_cleanup(struct _mosquitto_db *db, bool reload)
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

/*
 * Function: mosquitto_unpwd_init
 *
 * This function is called when the broker starts up. It should be used to
 * initialise data structures or connect to data providers relating to
 * usernames and passwords.  This may be unnecessary in some situations, for
 * example if a SQL server is used to store both username, password and ACL
 * information then one one of <mosquitto_acl_init> and <mosquitto_unpwd_init>
 * need be used.
 *
 * This function will also be called when the broker receives a signal to
 * reload its configuration. In this situation <mosquitto_unpwd_cleanup> will
 * be called followed by <mosquitto_unpwd_init>.
 *
 * Parameters:
 *	db - main broker data structer
 *	reload - set to true if this function is being called as part of a config
 *           reload.
 */
int mosquitto_unpwd_init(struct _mosquitto_db *db, bool reload)
{
	return MOSQ_ERR_SUCCESS;
}

/*
 * Function: mosquitto_unpwd_check
 *
 * This function is called to verify a username and password for authentication.
 * It is currently only called if the connecting client provides a username. If
 * you wish to prevent anonymous connections, use the allow_anonymous
 * configuration variable.
 *
 * Your function should be able to cope with the possibility of password being
 * NULL.
 *
 * Returns:
 *	MOSQ_ERR_SUCCESS - if the username/password was authenticated correctly.
 *	MOSQ_ERR_AUTH - if the username/password was denied.
 *	other - see lib/mosquitto.h for appropriate values.
 */
int mosquitto_unpwd_check(struct _mosquitto_db *db, const char *username, const char *password)
{
	return MOSQ_ERR_AUTH;
}

/*
 * Function: mosquitto_unpwd_cleanup
 *
 * This function is called when the broker shuts down. It should be used to
 * free data structures or disconnect from data providers relating to usernames
 * and passwords.
 *
 * This function will also be called when the broker receives a signal to
 * reload its configuration. In this situation <mosquitto_unpwd_cleanup> will be
 * called followed by <mosquitto_unpwd_init>.
 *
 * Parameters:
 *	db - main broker data structer
 *	reload - set to true if this function is being called as part of a config
 *           reload.
 */
int mosquitto_unpwd_cleanup(struct _mosquitto_db *db, bool reload)
{
	return MOSQ_ERR_SUCCESS;
}

#endif
