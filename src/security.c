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

#include <config.h>

#include <stdio.h>
#include <string.h>

#include <mosquitto_broker.h>
#include <memory_mosq.h>
#include "lib_load.h"

int mosquitto_security_module_init(mosquitto_db *db)
{
	void *lib;
	if(db->config->auth_plugin){
		lib = LIB_LOAD(db->config->auth_plugin);
		if(!lib) return 1;

		db->auth_plugin.lib = NULL;
		if(!(db->auth_plugin.plugin_init = LIB_SYM(lib, "mosquitto_auth_plugin_init"))){
			LIB_CLOSE(lib);
			return 1;
		}
		if(!(db->auth_plugin.plugin_cleanup = LIB_SYM(lib, "mosquitto_auth_plugin_cleanup"))){
			LIB_CLOSE(lib);
			return 1;
		}

		if(!(db->auth_plugin.security_init = LIB_SYM(lib, "mosquitto_auth_security_init"))){
			LIB_CLOSE(lib);
			return 1;
		}

		if(!(db->auth_plugin.security_apply = LIB_SYM(lib, "mosquitto_auth_security_apply"))){
			LIB_CLOSE(lib);
			return 1;
		}

		if(!(db->auth_plugin.security_cleanup = LIB_SYM(lib, "mosquitto_auth_security_cleanup"))){
			LIB_CLOSE(lib);
			return 1;
		}

		if(!(db->auth_plugin.acl_check = LIB_SYM(lib, "mosquitto_auth_acl_check"))){
			LIB_CLOSE(lib);
			return 1;
		}

		if(!(db->auth_plugin.unpwd_check = LIB_SYM(lib, "mosquitto_auth_unpwd_check"))){
			LIB_CLOSE(lib);
			return 1;
		}

		db->auth_plugin.lib = lib;
		if(db->auth_plugin.plugin_init){
			db->auth_plugin.plugin_init(db->config->auth_options, db->config->auth_option_count);
		}
	}else{
		db->auth_plugin.lib = NULL;
		db->auth_plugin.plugin_init = NULL;
		db->auth_plugin.plugin_cleanup = NULL;
		db->auth_plugin.security_init = NULL;
		db->auth_plugin.security_apply = NULL;
		db->auth_plugin.security_cleanup = NULL;
		db->auth_plugin.acl_check = NULL;
		db->auth_plugin.unpwd_check = NULL;
	}

	return MOSQ_ERR_SUCCESS;
}

int mosquitto_security_module_cleanup(mosquitto_db *db)
{
	if(db->auth_plugin.plugin_cleanup){
		db->auth_plugin.plugin_cleanup(db->config->auth_options, db->config->auth_option_count);
	}

	if(db->config->auth_plugin){
		if(db->auth_plugin.lib){
			LIB_CLOSE(db->auth_plugin.lib);
		}
	}
	db->auth_plugin.lib = NULL;
	db->auth_plugin.plugin_init = NULL;
	db->auth_plugin.plugin_cleanup = NULL;
	db->auth_plugin.security_init = NULL;
	db->auth_plugin.security_apply = NULL;
	db->auth_plugin.security_cleanup = NULL;
	db->auth_plugin.acl_check = NULL;
	db->auth_plugin.unpwd_check = NULL;

	return MOSQ_ERR_SUCCESS;
}

int mosquitto_security_init(mosquitto_db *db, bool reload)
{
	if(!db->auth_plugin.lib){
		return mosquitto_security_init_default(db, reload);
	}else{
		return db->auth_plugin.security_init(db->config->auth_options, db->config->auth_option_count, reload);
	}
}

/* Apply security settings after a reload.
 * Includes:
 * - Disconnecting anonymous users if appropriate
 * - Disconnecting users with invalid passwords
 * - Reapplying ACLs
 */
int mosquitto_security_apply(struct _mosquitto_db *db)
{
	if(!db->auth_plugin.lib){
		return mosquitto_security_apply_default(db);
	}else{
		return db->auth_plugin.security_apply(db->config->auth_options, db->config->auth_option_count);
	}
}

int mosquitto_security_cleanup(mosquitto_db *db, bool reload)
{
	if(!db->auth_plugin.lib){
		return mosquitto_security_cleanup_default(db, reload);
	}else{
		return db->auth_plugin.security_cleanup(db->config->auth_options, db->config->auth_option_count, reload);
	}
}

int mosquitto_acl_check(struct _mosquitto_db *db, struct mosquitto *context, const char *topic, int access)
{
	if(!db->auth_plugin.lib){
		return mosquitto_acl_check_default(db, context, topic, access);
	}else{
		return db->auth_plugin.acl_check(context->username, topic, access);
	}
}

int mosquitto_unpwd_check(struct _mosquitto_db *db, const char *username, const char *password)
{
	if(!db->auth_plugin.lib){
		return mosquitto_unpwd_check_default(db, username, password);
	}else{
		return db->auth_plugin.unpwd_check(username, password);
	}
}

