/*
Copyright (c) 2013 Roger Light <roger@atchoo.org>
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

#ifdef __APPLE__
#include <mach/mach.h>
#include <mach/mach_time.h>
#endif

#ifdef WIN32
#  define _WIN32_WINNT _WIN32_WINNT_VISTA
#  include <windows.h>
#else
#  include <unistd.h>
#endif
#include <time.h>

#ifdef WIN32
static bool tick64 = false;

void _windows_time_version_check(void)
{
	OSVERSIONINFO vi;

	tick64 = false;

	memset(vi, sizeof(OSVERSIONINFO));
	vi.dwOSVersionInfoSize = sizeof(OSVERSIONINFO);
	if(GetVersionEx(vi)){
		if(vi.dwMajorVersion > 5){
			tick64 = true;
		}
	}
}
#endif

time_t mosquitto_time_ms(void)
{
#ifdef WIN32
	if(tick64){
		return GetTickCount64();
	}else{
		return GetTickCount(); /* FIXME - need to deal with overflow. */
	}
#elif _POSIX_TIMERS>0 && defined(_POSIX_MONOTONIC_CLOCK)
	struct timespec tp;

	clock_gettime(CLOCK_MONOTONIC, &tp);
	return tp.tv_sec*1000 + tp.tv_nsec/100000;
#elif defined(__APPLE__)
	static mach_timebase_info_data_t tb;
    	uint64_t ticks;
	uint64_t milli;

	ticks = mach_absolute_time();

	if(tb.denom == 0){
		mach_timebase_info(&tb);
	}

	milli = ticks/1000000/tb.denom * tb.numer;

	return (time_t)milli;
#else
	return time(NULL)*1000;
#endif
}

time_t mosquitto_time_s(void)
{
	return mosquitto_time_ms()/1000;
}

time_t mosquitto_time_interval_ms(time_t *previous)
{
	time_t current = mosquitto_time_ms();
	time_t diff;

	diff = current - *previous;

#ifdef WIN32
	if(!tick64 && diff < 0){
		diff &= 0xFFFFFFFF;
	}
#endif
	*previous = current;

	return diff;
}

time_t mosquitto_time_interval_s(time_t *previous)
{
	time_t diff;

	*previous *= 1000;
	diff = mosquitto_time_interval_ms(previous);
	*previous /= 1000;

	return diff;
}

