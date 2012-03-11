#include <stdio.h>

#include <mosquitto.h>
#include <mysql/mysql.h>

MYSQL *mysql_connection;

int main(int argc, char *argv[])
{
	mysql_library_init(0, NULL, NULL);


	mysql_library_end();
	return 0;
}

