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

#ifdef WIN32

#include <windows.h>

#include <memory_mosq.h>

extern int run;
static SERVICE_STATUS_HANDLE service_handle;
static SERVICE_STATUS service_status;
int main(int argc, char *argv[]);

/* Service control callback */
void __stdcall service_handler(DWORD fdwControl)
{
	switch(fdwControl){
		case SERVICE_CONTROL_CONTINUE:
			/* Continue from Paused state. */
			break;
		case SERVICE_CONTROL_PAUSE:
			/* Pause service. */
			break;
		case SERVICE_CONTROL_SHUTDOWN:
			/* System is shutting down. */
		case SERVICE_CONTROL_STOP:
			/* Service should stop. */
			service_status.dwCurrentState = SERVICE_STOP_PENDING;
			SetServiceStatus(service_handle, &service_status);
			run = 0;
			break;
	}
}

/* Function called when started as a service. */
void __stdcall service_main(DWORD dwArgc, LPTSTR *lpszArgv)
{
	char **argv;
	int argc = 1;

	service_handle = RegisterServiceCtrlHandler("mosquitto", service_handler);
	if(service_handle){
		argv = _mosquitto_malloc(sizeof(char *)*3);
		argv[0] = "mosquitto";
		argv[1] = "-c";
		argv[2] = NULL; //FIXME path to mosquitto.conf - get from env var
		argc = 3;

		service_status.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
		service_status.dwCurrentState = SERVICE_RUNNING;
		service_status.dwControlsAccepted = SERVICE_ACCEPT_SHUTDOWN | SERVICE_ACCEPT_STOP;
		service_status.dwWin32ExitCode = NO_ERROR;
		service_status.dwCheckPoint = 0;
		SetServiceStatus(service_handle, &service_status);

		main(argc, argv);
		_mosquitto_free(argv);

		service_status.dwCurrentState = SERVICE_STOPPED;
		SetServiceStatus(service_handle, &service_status);
	}
}

void service_install(void)
{
	SC_HANDLE sc_manager, svc_handle;
	char exe_path[MAX_PATH + 5];

	GetModuleFileName(NULL, exe_path, MAX_PATH);
	strcat(exe_path, " run");

	sc_manager = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
	if(sc_manager){
		svc_handle = CreateService(sc_manager, "mosquitto", "mosquitto", 
				SERVICE_START | SERVICE_STOP,
				SERVICE_WIN32_OWN_PROCESS, SERVICE_AUTO_START, SERVICE_ERROR_NORMAL,
				exe_path, NULL, NULL, NULL, NULL, NULL);

		if(svc_handle){
			CloseServiceHandle(svc_handle);
		}
		CloseServiceHandle(sc_manager);
	}
}

void service_uninstall(void)
{
	SC_HANDLE sc_manager, svc_handle;
	SERVICE_STATUS status;

	sc_manager = OpenSCManager(NULL, SERVICES_ACTIVE_DATABASE, SC_MANAGER_CONNECT);
	if(sc_manager){
		svc_handle = OpenService(sc_manager, "mosquitto", SERVICE_QUERY_STATUS | DELETE);
		if(svc_handle){
			if(QueryServiceStatus(svc_handle, &status)){
				if(status.dwCurrentState == SERVICE_STOPPED){
					DeleteService(svc_handle);
				}
			}
			CloseServiceHandle(svc_handle);
		}
		CloseServiceHandle(sc_manager);
	}
}

void service_run(void)
{
	SERVICE_TABLE_ENTRY ste[] = {
		{ "mosquitto", service_main },
		{ NULL, NULL }
	};

	StartServiceCtrlDispatcher(ste);
}

#endif
