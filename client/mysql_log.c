#include <stdio.h>

#ifndef WIN32
#  include <unistd.h>
#else
#  include <process.h>
#  define snprintf sprintf_s
#endif

#include <mosquitto.h>
#include <mysql/mysql.h>

int main(int argc, char *argv[])
{
	MYSQL *connection;
	my_bool reconnect = true;
	char clientid[50];
	struct mosquitto *mosq;

	mysql_library_init(0, NULL, NULL);
	mosquitto_lib_init();

	connection = mysql_init(NULL);

	if(connection){
		mysql_options(connection, MYSQL_OPT_RECONNECT, &reconnect);

		snprintf(clientid, 50, "mysql_log_%d", getpid());
		mosq = mosquitto_new(clientid, connection);
		if(mosq){
			mosquitto_destroy(mosq);
		}

		mysql_close(connection);
	}

	mysql_library_end();
	mosquitto_lib_cleanup();

	return 0;
}

