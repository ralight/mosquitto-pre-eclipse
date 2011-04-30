include_directories(${mosquitto_SOURCE_DIR}/lib
			${STDBOOL_H_PATH} ${STDINT_H_PATH})
link_directories(${mosquitto_BINARY_DIR}/lib)

add_executable(mosquitto_control control_client.c)

target_link_libraries(mosquitto_control libmosquitto)

set_target_properties(mosquitto_control PROPERTIES
	VERSION ${VERSION})
install(TARGETS mosquitto_control RUNTIME DESTINATION ${BINDIR} LIBRARY DESTINATION ${LIBDIR})
