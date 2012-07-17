add_subdirectory(cpp)

include_directories(${mosquitto_SOURCE_DIR} ${mosquitto_SOURCE_DIR}/lib
			${STDBOOL_H_PATH} ${STDINT_H_PATH}
			${OPENSSL_INCLUDE_DIR})
link_directories(${mosquitto_SOURCE_DIR}/lib)

add_library(libmosquitto SHARED
	logging_mosq.c logging_mosq.h
	memory_mosq.c memory_mosq.h
	messages_mosq.c messages_mosq.h
	mosquitto.c mosquitto.h
	mqtt3_protocol.h
	net_mosq.c net_mosq.h
	read_handle.c read_handle.h
	read_handle_client.c
	read_handle_shared.c
	send_client_mosq.c
	send_mosq.c send_mosq.h
	thread_mosq.c
	util_mosq.c util_mosq.h
	will_mosq.c will_mosq.h)

option(WITH_THREADING
	"Include client library threading support?" ON)
if (${WITH_THREADING} STREQUAL ON AND NOT WIN32)
	add_definitions("-DWITH_THREADING")
	set (PTHREAD_LIBRARIES pthread)
else (${WITH_THREADING} STREQUAL ON AND NOT WIN32)
	set (PTHREAD_LIBRARIES "")
endif (${WITH_THREADING} STREQUAL ON AND NOT WIN32)

if (WIN32)
	target_link_libraries(libmosquitto ws2_32 ${OPENSSL_LIBRARIES})
else (WIN32)
	target_link_libraries(libmosquitto ${OPENSSL_LIBRARIES} ${PTHREAD_LIBRARIES})
endif (WIN32)

set_target_properties(libmosquitto PROPERTIES
	OUTPUT_NAME mosquitto
	VERSION ${VERSION}
	SOVERSION 1
)

install(TARGETS libmosquitto RUNTIME DESTINATION ${BINDIR} LIBRARY DESTINATION ${LIBDIR})
install(FILES mosquitto.h DESTINATION ${INCLUDEDIR})

if (UNIX)
	install(CODE "EXEC_PROGRAM(/sbin/ldconfig)")
endif (UNIX)
