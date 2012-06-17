# Copyright (c) 2012 Roger Light <roger@atchoo.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of mosquitto nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import select
import socket
import struct
import sys
import threading
import time

if sys.version_info[0] < 3:
    PROTOCOL_NAME = "MQIsdp"
else:
    PROTOCOL_NAME = b"MQIsdp"

PROTOCOL_VERSION = 3

# Message types 
CONNECT = 0x10
CONNACK = 0x20
PUBLISH = 0x30
PUBACK = 0x40
PUBREC = 0x50
PUBREL = 0x60
PUBCOMP = 0x70
SUBSCRIBE = 0x80
SUBACK = 0x90
UNSUBSCRIBE = 0xA0
UNSUBACK = 0xB0
PINGREQ = 0xC0
PINGRESP = 0xD0
DISCONNECT = 0xE0

# Log levels
MOSQ_LOG_INFO = 0x01
MOSQ_LOG_NOTICE = 0x02
MOSQ_LOG_WARNING = 0x04
MOSQ_LOG_ERR = 0x08
MOSQ_LOG_DEBUG = 0x10

# CONNACK codes
CONNACK_ACCEPTED = 0
CONNACK_REFUSED_PROTOCOL_VERSION = 1
CONNACK_REFUSED_IDENTIFIER_REJECTED = 2
CONNACK_REFUSED_SERVER_UNAVAILABLE = 3
CONNACK_REFUSED_BAD_USERNAME_PASSWORD = 4
CONNACK_REFUSED_NOT_AUTHORIZED = 5

# Connection state
mosq_cs_new = 0
mosq_cs_connected = 1
mosq_cs_disconnecting = 2
mosq_cs_connect_async = 3

# Message direction
mosq_md_invalid = 0
mosq_md_in = 1
mosq_md_out = 2

# Message state
mosq_ms_invalid = 0,
mosq_ms_wait_puback = 1
mosq_ms_wait_pubrec = 2
mosq_ms_wait_pubrel = 3
mosq_ms_wait_pubcomp = 4

# Error values
MOSQ_ERR_AGAIN = -1
MOSQ_ERR_SUCCESS = 0
MOSQ_ERR_NOMEM = 1
MOSQ_ERR_PROTOCOL = 2
MOSQ_ERR_INVAL = 3
MOSQ_ERR_NO_CONN = 4
MOSQ_ERR_CONN_REFUSED = 5
MOSQ_ERR_NOT_FOUND = 6
MOSQ_ERR_CONN_LOST = 7
MOSQ_ERR_SSL = 8
MOSQ_ERR_PAYLOAD_SIZE = 9
MOSQ_ERR_NOT_SUPPORTED = 10
MOSQ_ERR_AUTH = 11
MOSQ_ERR_ACL_DENIED = 12
MOSQ_ERR_UNKNOWN = 13
MOSQ_ERR_ERRNO = 14


class MosquittoMessage:
    def __init__(self):
        self.timestamp = 0
        self.direction = mosq_md_invalid
        self.state = mosq_ms_invalid
        self.dup = False
        self.mid = 0
        self.topic = ""
        self.payload = None
        self.qos = 0
        self.retain = False

class MosquittoInPacket:
    def __init__(self):
        self.command = 0
        self.have_remaining = 0
        self.remaining_count = []
        self.remaining_mult = 1
        self.remaining_length = 0
        self.packet = b""
        self.to_process = 0
        self.pos = 0

    def cleanup(self):
        self.__init__()

class MosquittoPacket:
    def __init__(self, command, packet, mid, qos):
        self.command = command
        self.mid = mid
        self.qos = qos
        self.pos = 0
        self.to_process = len(packet)
        self.packet = packet

class Mosquitto:
    def __init__(self, client_id="", clean_session=True, obj=None):
        if clean_session == False and client_id == "":
            raise ValueError('A client id must be provided if clean session is False.')

        self._obj = None
        self._sock = None
        self._keepalive = 60
        self._message_retry = 20
        self._last_retry_check = 0
        self._clean_session = clean_session
        if client_id == "":
            self._id = "mosq/" + "".join(random.choice("0123456789ADCDEF") for x in range(23-5))
        else:
            self._client_id = client_id

        self._username = ""
        self._password = ""
        self._in_packet = MosquittoInPacket()
        self._out_packet = []
        self._last_msg_in = time.time()
        self._last_msg_out = time.time()
        self._ping_t = 0
        self._last_mid = 0
        self._state = mosq_cs_new
        self._messages = []
        self._will = False
        self._will_topic = ""
        self._will_payload = None
        self._will_qos = 0
        self._will_retain = False
        self.on_disconnect = None
        self.on_connect = None
        self.on_publish = None
        self.on_message = None
        self.on_subscribe = None
        self.on_unsubscribe = None
        self.on_log = None
        self._host = ""
        self._port = 1883
        self._in_callback = False
        self._strict_protocol = False
        self._callback_mutex = threading.Lock()
        self._state_mutex = threading.Lock()
        self._out_packet_mutex = threading.Lock()
        self._current_out_packet_mutex = threading.Lock()
        self._msgtime_mutex = threading.Lock()
        self._thread = None
        self._thread_terminate = False

    def __del__(self):
        pass

    def connect(self, host, port=1883, keepalive=60):
        self.connect_async(host, port, keepalive)
        return self.reconnect()

    def connect_async(self, host, port=1883, keepalive=60):
        if host == None or len(host) == 0:
            raise ValueError('Invalid host.')
        if port <= 0:
            raise ValueError('Invalid port number.')
        if keepalive < 0:
            raise ValueError('Keepalive must be >=0.')

        self._host = host
        self._port = port
        self._keepalive = keepalive

        self._state_mutex.acquire()
        self._state = mosq_cs_connect_async
        self._state_mutex.release()

    def reconnect(self):
        if len(self._host) == 0:
            raise ValueError('Invalid host.')
        if self._port <= 0:
            raise ValueError('Invalid port number.')

        self._state_mutex.acquire()
        self._state = mosq_cs_new
        self._state_mutex.release()
        if self._sock:
            self._sock.close()
            self._sock = None

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # FIXME use create_connection here

        self._sock.connect((self._host, self._port))
        self._sock.setblocking(0)
        return self._send_connect(self._keepalive, self._clean_session)

    def loop(self, timeout=1.0, max_packets=1):
        if timeout < 0.0:
            raise ValueError('Invalid timeout.')

        if len(self._out_packet) > 0:
            wlist = [self._sock]
        else:
            wlist = []

        rlist = [self._sock]
        socklist = select.select(rlist, wlist, [], timeout)

        if self._sock in socklist[0]:
            rc = self.loop_read(max_packets)
            if rc != MOSQ_ERR_SUCCESS:
                self._sock.close()
                self._sock = None
                self._state_mutex.acquire()
                if self._state == mosq_cs_disconnecting:
                    rc = MOSQ_ERR_SUCCESS
                self._state_mutex.release()
                self._callback_mutex.acquire()
                if self.on_disconnect:
                    self._in_callback = True
                    self.on_disconnect(self, self._obj, rc)
                    self._in_callback = False

                self._callback_mutex.release()
                return rc

        if self._sock in socklist[1]:
            rc = self.loop_write(max_packets)
            if rc != MOSQ_ERR_SUCCESS:
                self._sock.close()
                self._sock = None
                self._state_mutex.acquire()
                if self._state == mosq_cs_disconnecting:
                    rc = MOSQ_ERR_SUCCESS
                self._state_mutex.release()
                self._callback_mutex.acquire()
                if self.on_disconnect:
                    self._in_callback = True
                    self.on_disconnect(self, self._obj, rc)
                    self._in_callback = False
                self._callback_mutex.release()
                return rc

        return self.loop_misc()

    def publish(self, topic, payload=None, qos=0, retain=False):
        if len(topic) == 0:
            raise ValueError('Invalid topic.')
        if qos<0 or qos>2:
            raise ValueError('Invalid QoS level.')
        if payload != None and len(payload) > 268435455:
            raise ValueError('Payload too large.')

        if self._topic_wildcard_len_check(topic) != MOSQ_ERR_SUCCESS:
            raise ValueError('Publish topic cannot contain wildcards.')

        local_mid = self._mid_generate()

        if qos == 0:
            rc = self._send_publish(local_mid, topic, payload, qos, retain, False)
            return (rc, local_mid)
        else:
            message = MosquittoMessage()
            message.timestamp = time.time()
            message.direction = mosq_md_out
            if qos == 1:
                message.state = mosq_ms_wait_puback
            elif qos == 2:
                message.state = mosq_ms_wait_pubrec

            message.mid = local_mid
            message.topic = topic
            if payload == None or len(payload) == 0:
                message.payload = None
            else:
                message.payload = payload

            message.qos = qos
            message.retain = retain
            message.dup = False

            self._messages.append(message)
            rc = self._send_publish(message.mid, message.topic, message.payload, message.qos, message.retain, message.dup)
            return (rc, local_mid)

    def username_pw_set(self, username, password=None):
        self._username = username
        self._password = password

    def disconnect(self):
        if self._sock == None:
            return MOSQ_ERR_NO_CONN

        self._state_mutex.acquire()
        self._state = mosq_cs_disconnecting
        self._state_mutex.release()

        return self._send_disconnect()
    
    def subscribe(self, topic, qos=0):
        if qos<0 or qos>2:
            raise ValueError('Invalid QoS level.')
        if topic == None or len(topic) == 0:
            raise ValueError('Invalid topic.')

        if self._sock == None:
            return MOSQ_ERR_NO_CONN

        return self._send_subscribe(False, topic, qos)

    def unsubscribe(self, topic):
        if topic == None or len(topic) == 0:
            raise ValueError('Invalid topic.')
        if self._sock == None:
            return MOSQ_ERR_NO_CONN

        return self._send_unsubscribe(False, topic)

    def loop_read(self, max_packets=1):
        if self._sock == None:
            return MOSQ_ERR_NO_CONN

        if max_packets < 1:
            raise ValueError('Invalid max_packets.')

        for i in range(0, max_packets):
            rc = self._packet_read()
            if rc > 0:
                return rc
            elif rc == MOSQ_ERR_AGAIN:
                return MOSQ_ERR_SUCCESS
        return MOSQ_ERR_SUCCESS

    def loop_write(self, max_packets=1):
        if self._sock == None:
            return MOSQ_ERR_NO_CONN

        if max_packets < 1:
            raise ValueError('Invalid max_packets.')

        for i in range(0, max_packets):
            rc = self._packet_write()
            if rc > 0:
                return rc
            elif rc == MOSQ_ERR_AGAIN:
                return MOSQ_ERR_SUCCESS
        return MOSQ_ERR_SUCCESS

    def want_write(self):
        if self._out_packet == None:
            return False
        else:
            return True

    def loop_misc(self):
        if self._sock == None:
            return MOSQ_ERR_NO_CONN

        now = time.time()
        self._check_keepalive()
        if self._last_retry_check+1 < now:
            # Only check once a second at most
            self._message_retry_check()
            self._last_retry_check = now

        if self._ping_t > 0 and now - self._ping_t >= self._keepalive:
            # mosq->ping_t != 0 means we are waiting for a pingresp.
            # This hasn''t happened in the keepalive time so we should disconnect.
            self._sock.close()
            self._sock = None
            return MOSQ_ERR_CONN_LOST

        return MOSQ_ERR_SUCCESS

    def message_retry_set(self, retry):
        if retry < 0:
            raise ValueError('Invalid retry.')

        self._message_retry = retry

    def user_data_set(self, obj):
        self._obj = obj

    def will_set(self, topic, payload=None, qos=0, retain=False):
        if topic == None or len(topic) == 0:
            raise ValueError('Invalid topic.')
        if qos<0 or qos>2:
            raise ValueError('Invalid QoS level.')
        if isinstance(payload, str) == False and isinstance(payload, bytearray) == False:
            raise TypeError('payload must be a string or a bytearray.')

        self._will = True
        self._will_topic = topic
        self._will_payload = payload
        self._will_qos = qos
        self._will_retain = retain

    def will_clear(self):
        self._will = False
        self._will_topic = ""
        self._will_payload = None
        self._will_qos = 0
        self._will_retain = False

    def error_string(self, mosq_errno):
        if mosq_errno == MOSQ_ERR_SUCESS:
            return "No error."
        elif mosq_errno == MOSQ_ERR_NOMEM:
            return "Out of memory."
        elif mosq_errno == MOSQ_ERR_PROTOCOL:
            return "A network protocol error occurred when communicating with the broker."
        elif mosq_errno == MOSQ_ERR_INVAL:
            return "Invalid function arguments provided."
        elif mosq_errno == MOSQ_ERR_NO_CONN:
            return "The client is not currently connected."
        elif mosq_errno == MOSQ_ERR_CONN_REFUSED:
            return "The connection was refused."
        elif mosq_errno == MOSQ_ERR_NOT_FOUND:
            return "Message not found (internal error)."
        elif mosq_errno == MOSQ_ERR_CONN_LOST:
            return "The connection was lost."
        elif mosq_errno == MOSQ_ERR_SSL:
            return "An SSL error occurred."
        elif mosq_errno == MOSQ_ERR_PAYLOAD_SIZE:
            return "Payload too large."
        elif mosq_errno == MOSQ_ERR_NOT_SUPPORTED:
            return "This feature is not supported."
        elif mosq_errno == MOSQ_ERR_AUTH:
            return "Authorisation failed."
        elif mosq_errno == MOSQ_ERR_ACL_DENIED:
            return "Access denied by ACL."
        elif mosq_errno == MOSQ_ERR_UNKNOWN:
            return "Unknown error."
        elif mosq_errno == MOSQ_ERR_ERRNO:
            return "Error defined by errno."
        else:
            return "Unknown error."

    def connack_string(self, connack_code):
        if connack_code == 0:
            return "Connection Accepted."
        elif connack_code == 1:
            return "Connection Refused: unacceptable protocol version."
        elif connack_code == 2:
            return "Connection Refused: identifier rejected."
        elif connack_code == 3:
            return "Connection Refused: broker unavailable."
        elif connack_code == 4:
            return "Connection Refused: bad user name or password."
        elif connack_code == 5:
            return "Connection Refused: not authorised."
        else:
            return "Connection Refused: unknown reason."

    def socket(self):
        return self._sock

    def loop_start(self):
        if self._thread != None:
            return MOSQ_ERR_INVAL

        self._thread = threading.Thread(target=self._thread_main)
        self._thread.daemon = True
        self._thread.start()

    def loop_stop(self, force=False):
        if self._thread == None:
            return MOSQ_ERR_INVAL

        self._thread_terminate = True
        self._thread.join()
        self._thread = None

    # ============================================================
    # Private functions
    # ============================================================

    def _packet_read(self):
        # This gets called if pselect() indicates that there is network data
        # available - ie. at least one byte.  What we do depends on what data we
        # already have.
        # If we've not got a command, attempt to read one and save it. This should
        # always work because it's only a single byte.
        # Then try to read the remaining length. This may fail because it is may
        # be more than one byte - will need to save data pending next read if it
        # does fail.
        # Then try to read the remaining payload, where 'payload' here means the
        # combined variable header and actual payload. This is the most likely to
        # fail due to longer length, so save current data and current position.
        # After all data is read, send to _mosquitto_handle_packet() to deal with.
        # Finally, free the memory and reset everything to starting conditions.
        if self._in_packet.command == 0:
            try:
                command = self._sock.recv(1)
            except socket.error as err:
                (msg) = err
                if msg.errno == 11:
                    return MOSQ_ERR_AGAIN
                print(msg)
                return 1
            else:
                if len(command) == 0:
                    return 1
                command = struct.unpack("!B", command)
                self._in_packet.command = command[0]

        if self._in_packet.have_remaining == 0:
            # Read remaining
            # Algorithm for decoding taken from pseudo code at
            # http://publib.boulder.ibm.com/infocenter/wmbhelp/v6r0m0/topic/com.ibm.etools.mft.doc/ac10870_.htm
            while True:
                try:
                    byte = self._sock.recv(1)
                except socket.error as err:
                    (msg) = err
                    if msg.errno == 11:
                        return MOSQ_ERR_AGAIN
                    print(msg)
                    return 1
                else:
                    byte = struct.unpack("!B", byte)
                    byte = byte[0]
                    self._in_packet.remaining_count.append(byte)
                    # Max 4 bytes length for remaining length as defined by protocol.
                     # Anything more likely means a broken/malicious client.
                    if len(self._in_packet.remaining_count) > 4:
                        return MOSQ_ERR_PROTOCOL

                    self._in_packet.remaining_length = self._in_packet.remaining_length + (byte & 127)*self._in_packet.remaining_mult
                    self._in_packet.remaining_mult = self._in_packet.remaining_mult * 128

                if (byte & 128) == 0:
                    break

            self._in_packet.have_remaining = 1
            self._in_packet.to_process = self._in_packet.remaining_length

        while self._in_packet.to_process > 0:
            try:
                data = self._sock.recv(self._in_packet.to_process)
            except socket.error as err:
                (msg) = err
                if msg.errno == 11:
                    return MOSQ_ERR_AGAIN
                print(msg)
                return 1
            else:
                self._in_packet.to_process = self._in_packet.to_process - len(data)
                self._in_packet.packet = self._in_packet.packet + data

        # All data for this packet is read.
        self._in_packet.pos = 0
        rc = self._packet_handle()

        # Free data and reset values 
        self._in_packet.cleanup()

        self._msgtime_mutex.acquire()
        self._last_msg_in = time.time()
        self._msgtime_mutex.release()
        return rc

    def _packet_write(self):
        while len(self._out_packet) > 0:
            packet = self._out_packet[0]

            write_length = self._sock.send(packet.packet[packet.pos:])
            if write_length > 0:
                packet.to_process = packet.to_process - write_length
                packet.pos = packet.pos + write_length

                if packet.to_process == 0:
                    if (packet.command & 0xF0) == PUBLISH and packet.qos == 0:
                        self._callback_mutex.acquire()
                        if self.on_publish:
                            self._in_callback = True
                            self.on_publish(self, self._obj, packet.mid)
                            self._in_callback = False

                        self._callback_mutex.release()

                    self._out_packet.pop(0)
            else:
                pass # FIXME
        
        return MOSQ_ERR_SUCCESS

    def _easy_log(self, level, buf):
        if self.on_log:
            self.on_log(level, buf)

    def _check_keepalive(self):
        now = time.time()
        self._msgtime_mutex.acquire()
        last_msg_out = self._last_msg_out
        last_msg_in = self._last_msg_in
        self._msgtime_mutex.release()
        if self._sock != None and (now - last_msg_out >= self._keepalive or now - last_msg_in >= self._keepalive):
            if self._state == mosq_cs_connected and self._ping_t == 0:
                self._send_pingreq()
            else:
                self._sock.close()
                self._sock = None

    def _fix_sub_topic(self, subtopic):
        # Convert ////some////over/slashed///topic/etc/etc//
         # into some/over/slashed/topic/etc/etc
        pass
        # FIXME
        #char *fixed = NULL
        #char *token
        #char *saveptr = NULL

        #assert(subtopic)
        #assert(*subtopic)

        #/* size of fixed here is +1 for the terminating 0 and +1 for the spurious /
         #* that gets appended. */
        #fixed = _mosquitto_calloc(strlen(*subtopic)+2, 1)
        #if(!fixed) return MOSQ_ERR_NOMEM

        #if((*subtopic)[0] == '/'){
            #fixed[0] = '/'
        #}
        #token = strtok_r(*subtopic, "/", &saveptr)
        #while(token){
            #strcat(fixed, token)
            #strcat(fixed, "/")
            #token = strtok_r(NULL, "/", &saveptr)
        #}

        #fixed[strlen(fixed)-1] = '\0'
        #_mosquitto_free(*subtopic)
        #*subtopic = fixed
        #return MOSQ_ERR_SUCCESS

    def _mid_generate(self):
        self._last_mid = self._last_mid + 1
        if self._last_mid == 65536:
            self._last_mid = 1
        return self._last_mid

    def _topic_wildcard_len_check(self, topic):
        # Search for + or # in a topic. Return MOSQ_ERR_INVAL if found.
         # Also returns MOSQ_ERR_INVAL if the topic string is too long.
         # Returns MOSQ_ERR_SUCCESS if everything is fine.
        if '+' in topic or '#' in topic or len(topic) == 0 or len(topic) > 65535:
            return MOSQ_ERR_INVAL
        else:
            return MOSQ_ERR_SUCCESS

    def _send_pingreq(self):
        self._easy_log(MOSQ_LOG_DEBUG, "Sending PINGREQ")
        rc = self._send_simple_command(PINGREQ)
        if rc == MOSQ_ERR_SUCCESS:
            self._ping_t = time.time()
        return rc

    def _send_pingresp(self):
        self._easy_log(MOSQ_LOG_DEBUG, "Sending PINGRESP")
        return self._send_simple_command(PINGRESP)

    def _send_puback(self, mid):
        self._easy_log(MOSQ_LOG_DEBUG, "Sending PUBACK (Mid: "+str(mid)+")")
        return self._send_command_with_mid(PUBACK, mid, False)

    def _send_pubcomp(self, mid):
        self._easy_log(MOSQ_LOG_DEBUG, "Sending PUBCOMP (Mid: "+str(mid)+")")
        return self._send_command_with_mid(PUBCOMP, mid, False)

    def _pack_remaining_length(self, packet, remaining_length):
        remaining_bytes = []
        while True:
            byte = remaining_length % 128
            remaining_length = remaining_length // 128
            # If there are more digits to encode, set the top bit of this digit
            if remaining_length > 0:
                byte = byte | 0x80

            remaining_bytes.append(byte)
            packet.extend(struct.pack("!B", byte))
            if remaining_length == 0:
                # FIXME - this doesn't deal with incorrectly large payloads
                return packet

    def _pack_str16(self, packet, data):
        if sys.version_info[0] < 3:
            if isinstance(data, bytearray):
                packet.extend(struct.pack("!H", len(data)))
                packet.extend(data)
            elif isinstance(data, str):
                pack_format = "!H" + str(len(data)) + "s"
                packet.extend(struct.pack(pack_format, len(data), data))
            elif isinstance(data, unicode):
                udata = data.encode('utf-8')
                pack_format = "!H" + str(len(udata)) + "s"
                packet.extend(struct.pack(pack_format, len(udata), udata))
            else:
                raise TypeError
        else:
            if isinstance(data, bytearray):
                packet.extend(struct.pack("!H", len(data)))
                packet.extend(data)
            elif isinstance(data, str):
                udata = data.encode('utf-8')
                pack_format = "!H" + str(len(udata)) + "s"
                packet.extend(struct.pack(pack_format, len(udata), udata))
            else:
                raise TypeError

    def _send_publish(self, mid, topic, payload=None, qos=0, retain=False, dup=False):
        if self._sock == None:
            return MOSQ_ERR_NO_CONN

        command = PUBLISH | ((dup&0x1)<<3) | (qos<<1) | retain
        packet = bytearray()
        packet.extend(struct.pack("!B", command))
        if payload == None:
            remaining_length = 2+len(topic)
            self._easy_log(MOSQ_LOG_DEBUG, "Sending PUBLISH (d"+str(dup)+", q"+str(qos)+", r"+str(retain)+", m"+str(mid)+", '"+topic+"' (NULL payload)")
        else:
            remaining_length = 2+len(topic) + len(payload)
            self._easy_log(MOSQ_LOG_DEBUG, "Sending PUBLISH (d"+str(dup)+", q"+str(qos)+", r"+str(retain)+", m"+str(mid)+", '"+topic+"', ... ("+str(len(payload))+" bytes)")

        if qos > 0:
            # For message id
            remaining_length = remaining_length + 2

        self._pack_remaining_length(packet, remaining_length)
        self._pack_str16(packet, topic)

        if qos > 0:
            # For message id
            packet.extend(struct.pack("!H", mid))

        if payload != None:
            if isinstance(payload, str):
                if sys.version_info[0] < 3:
                    pack_format = str(len(payload)) + "s"
                    packet.extend(struct.pack(pack_format, payload))
                else:
                    upayload = payload.encode('utf-8')
                    pack_format = str(len(upayload)) + "s"
                    packet.extend(struct.pack(pack_format, upayload))
            elif isinstance(payload, bytearray):
                packet.extend(payload)
            elif isinstance(payload, unicode):
                    upayload = payload.encode('utf-8')
                    pack_format = str(len(upayload)) + "s"
                    packet.extend(struct.pack(pack_format, upayload))
            else:
                raise TypeError('payload must be a string, unicode or a bytearray.')

        return self._packet_queue(PUBLISH, packet, mid, qos)

    def _send_pubrec(self, mid):
        self._easy_log(MOSQ_LOG_DEBUG, "Sending PUBREC (Mid: "+str(mid)+")")
        return self._send_command_with_mid(PUBREC, mid, False)

    def _send_pubrel(self, mid, dup=False):
        self._easy_log(MOSQ_LOG_DEBUG, "Sending PUBREL (Mid: "+str(mid)+")")
        return self._send_command_with_mid(PUBREL|2, mid, dup)

    def _send_command_with_mid(self, command, mid, dup):
        # For PUBACK, PUBCOMP, PUBREC, and PUBREL
        if dup:
            command = command | 8

        remaining_length = 2
        packet = struct.pack('!BBH', command, remaining_length, mid)
        return self._packet_queue(command, packet, mid, 1)

    def _send_simple_command(self, command):
        # For DISCONNECT, PINGREQ and PINGRESP
        remaining_length = 0
        packet = struct.pack('!BB', command, remaining_length)
        return self._packet_queue(command, packet, 0, 0)

    def _send_connect(self, keepalive, clean_session):
        remaining_length = 12 + 2+len(self._client_id)
        connect_flags = 0
        if clean_session:
            connect_flags = connect_flags | 0x02

        if self._will:
            remaining_length = remaining_length + 2+len(self._will_topic) + 2+len(self._will_payload)
            connect_flags = connect_flags | 0x04 | ((self._will_qos&0x03) << 3) | ((self._will_retain&0x01) << 5)

        if self._username:
            remaining_length = remaining_length + 2+len(self._username)
            connect_flags = connect_flags | 0x80
            if self._password:
                connect_flags = connect_flags | 0x40
                remaining_length = remaining_length + 2+len(self._password)

        command = CONNECT
        packet = bytearray()
        packet.extend(struct.pack("!B", command))
        self._pack_remaining_length(packet, remaining_length)
        packet.extend(struct.pack("!H6sBBH", len(PROTOCOL_NAME), PROTOCOL_NAME, PROTOCOL_VERSION, connect_flags, keepalive))

        self._pack_str16(packet, self._client_id)

        if self._will:
            self._pack_str16(packet, self._will_topic)
            if len(self._will_payload) > 0:
                self._pack_str16(packet, self._will_payload)
            else:
                packet.extend(struct.pack("!H", 0))

        if self._username:
            self._pack_str16(packet, self._username)

            if self._password:
                self._pack_str16(packet, self._password)

        self._keepalive = keepalive
        return self._packet_queue(command, packet, 0, 0)

    def _send_disconnect(self):
        return self._send_simple_command(DISCONNECT)

    def _send_subscribe(self, dup, topic, topic_qos):
        remaining_length = 2 + 2+len(topic) + 1
        command = SUBSCRIBE | (dup<<3) | (1<<1)
        packet = bytearray()
        packet.extend(struct.pack("!B", command))
        self._pack_remaining_length(packet, remaining_length)
        local_mid = self._mid_generate()
        pack_format = "!HH" + str(len(topic)) + "sB"
        packet.extend(struct.pack("!H", local_mid))
        self._pack_str16(packet, topic)
        packet.extend(struct.pack("B", topic_qos))
        return (self._packet_queue(command, packet, local_mid, 1), local_mid)

    def _send_unsubscribe(self, dup, topic):
        remaining_length = 2 + 2+len(topic)
        command = UNSUBSCRIBE | (dup<<3) | (1<<1)
        packet = bytearray()
        packet.extend(struct.pack("!B", command))
        self._pack_remaining_length(packet, remaining_length)
        local_mid = self._mid_generate()
        pack_format = "!HH" + str(len(topic)) + "sB"
        packet.extend(struct.pack("!H", local_mid))
        self._pack_str16(packet, topic)
        return (self._packet_queue(command, packet, local_mid, 1), local_mid)

    def _message_update(self, mid, direction, state):
        for m in self._messages:
            if m.mid == mid and m.direction == direction:
                m.state = state
                m.timestamp = time.time()
                return MOSQ_ERR_SUCCESS

        return MOSQ_ERR_NOT_FOUND

    def _message_retry_check(self):
        now = time.time()
        for m in self._messages:
            if m.timestamp + self._message_retry < now:
                if m.state == mosq_ms_wait_puback or m.state == mosq_ms_wait_pubrec:
                    m.timestamp = now
                    m.dup = True
                    self._send_publish(m.mid, m.topic, m.payload, m.qos, m.retain, m.dup)
                elif m.state == mosq_ms_wait_pubrel:
                    m.timestamp = now
                    m.dup = True
                    self._send_pubrec(m.mid)
                elif m.state == mosq_ms_wait_pubcomp:
                    m.timestamp = now
                    m.dup = True
                    self._send_pubrel(m.mid, True)

    def _packet_queue(self, command, packet, mid, qos):
        mpkt = MosquittoPacket(command, packet, mid, qos)
        self._out_packet_mutex.acquire()
        self._out_packet.append(mpkt)
        self._out_packet_mutex.release()

        if self._in_callback == False:
            return self.loop_write()
        else:
            return MOSQ_ERR_SUCCESS

    def _packet_handle(self):
        cmd = self._in_packet.command&0xF0
        if cmd == PINGREQ:
            return self._handle_pingreq()
        elif cmd == PINGRESP:
            return self._handle_pingresp()
        elif cmd == PUBACK:
            return self._handle_pubackcomp("PUBACK")
        elif cmd == PUBCOMP:
            return self._handle_pubackcomp("PUBCOMP")
        elif cmd == PUBLISH:
            return self._handle_publish()
        elif cmd == PUBREC:
            return self._handle_pubrec()
        elif cmd == PUBREL:
            return self._handle_pubrel()
        elif cmd == CONNACK:
            return self._handle_connack()
        elif cmd == SUBACK:
            return self._handle_suback()
        elif cmd == UNSUBACK:
            return self._handle_unsuback()
        else:
            # If we don't recognise the command, return an error straight away.
            self._easy_log(MOSQ_LOG_ERR, "Error: Unrecognised command "+str(cmd))
            return MOSQ_ERR_PROTOCOL

    def _handle_pingreq(self):
        if self._strict_protocol:
            if self._in_packet.remaining_length != 0:
                return MOSQ_ERR_PROTOCOL
        
        self._easy_log(MOSQ_LOG_DEBUG, "Received PINGREQ")
        return self._send_pingresp()

    def _handle_pingresp(self):
        if self._strict_protocol:
            if self._in_packet.remaining_length != 0:
                return MOSQ_ERR_PROTOCOL
        
        # No longer waiting for a PINGRESP.
        self._ping_t = 0
        self._easy_log(MOSQ_LOG_DEBUG, "Received PINGRESP")
        return MOSQ_ERR_SUCCESS

    def _handle_connack(self):
        if self._strict_protocol:
            if self._in_packet.remaining_length != 2:
                return MOSQ_ERR_PROTOCOL

        if len(self._in_packet.packet) != 2:
            return MOSQ_ERR_PROTOCOL

        (resvd, result) = struct.unpack("!BB", self._in_packet.packet)
        self._easy_log(MOSQ_LOG_DEBUG, "Received CONNACK ("+str(resvd)+", "+str(result)+")")
        self._callback_mutex.acquire()
        if self.on_connect:
            self._in_callback = True
            self.on_connect(self, self._obj, result)
            self._in_callback = False
        self._callback_mutex.release()
        if result == 0:
            self._state = mosq_cs_connected
            return MOSQ_ERR_SUCCESS
        elif result > 0 and result < 6:
            return MOSQ_ERR_CONN_REFUSED
        else:
            return MOSQ_ERR_PROTOCOL

    def _handle_suback(self):
        self._easy_log(MOSQ_LOG_DEBUG, "Received SUBACK")
        pack_format = "!H" + str(len(self._in_packet.packet)-2) + 's'
        (mid, packet) = struct.unpack(pack_format, self._in_packet.packet)
        pack_format = "!" + "B"*len(packet)
        granted_qos = struct.unpack(pack_format, packet)

        self._callback_mutex.acquire()
        if self.on_subscribe:
            self._in_callback = True
            self.on_subscribe(self, self._obj, mid, granted_qos)
            self._in_callback = False
        self._callback_mutex.release()

        return MOSQ_ERR_SUCCESS

    def _handle_publish(self):
        rc = 0

        header = self._in_packet.command
        message = MosquittoMessage()
        message.direction = mosq_md_in
        message.dup = (header & 0x08)>>3
        message.qos = (header & 0x06)>>1
        message.retain = (header & 0x01)

        pack_format = "!H" + str(len(self._in_packet.packet)-2) + 's'
        (slen, packet) = struct.unpack(pack_format, self._in_packet.packet)
        pack_format = '!' + str(slen) + 's' + str(len(packet)-slen) + 's'
        (message.topic, packet) = struct.unpack(pack_format, packet)

        rc = self._fix_sub_topic(message.topic)
        if len(message.topic) == 0:
            return MOSQ_ERR_PROTOCOL

        if sys.version_info[0] >= 3:
            message.topic = message.topic.decode('utf-8')

        if message.qos > 0:
            pack_format = "!H" + str(len(packet)-2) + 's'
            (message.mid, packet) = struct.unpack(pack_format, packet)

        message.payload = packet

        self._easy_log(MOSQ_LOG_DEBUG, "Received PUBLISH (d"+str(message.dup)+
                ", q"+str(message.qos)+", r"+str(message.retain)+
                ", m"+str(message.mid)+", '"+message.topic+
                "', ...  ("+str(len(message.payload))+" bytes)")

        message.timestamp = time.time()
        if message.qos == 0:
            self._callback_mutex.acquire()
            if self.on_message:
                self._in_callback = True
                self.on_message(self, self._obj, message)
                self._in_callback = False

            self._callback_mutex.release()
            return MOSQ_ERR_SUCCESS
        elif message.qos == 1:
            rc = self._send_puback(message.mid)
            self._callback_mutex.acquire()
            if self.on_message:
                self._in_callback = True
                self.on_message(self, self._obj, message)
                self._in_callback = False

            self._callback_mutex.release()
            return rc
        elif message.qos == 2:
            rc = self._send_pubrec(message.mid)
            message.state = mosq_ms_wait_pubrel
            self._messages.append(message)
            return rc
        else:
            return MOSQ_ERR_PROTOCOL

    def _handle_pubrel(self):
        if self._strict_protocol:
            if self._in_packet.remaining_length != 2:
                return MOSQ_ERR_PROTOCOL
        
        if len(self._in_packet.packet) != 2:
            return MOSQ_ERR_PROTOCOL

        mid = struct.unpack("!H", self._in_packet.packet)
        mid = mid[0]
        self._easy_log(MOSQ_LOG_DEBUG, "Received PUBREL (Mid: "+str(mid)+")")
        
        for i in range(len(self._messages)):
            if self._messages[i].direction == mosq_md_in and self._messages[i].mid == mid:

                # Only pass the message on if we have removed it from the queue - this
                # prevents multiple callbacks for the same message.
                self._callback_mutex.acquire()
                if self.on_message:
                    self._in_callback = True
                    self.on_message(self, self._obj, self._messages[i])
                    self._in_callback = False
                self._callback_mutex.release()
                self._messages.pop(i)

                return self._send_pubcomp(mid)

        return MOSQ_ERR_SUCCESS

    def _handle_pubrec(self):
        if self._strict_protocol:
            if self._in_packet.remaining_length != 2:
                return MOSQ_ERR_PROTOCOL
        
        mid = struct.unpack("!H", self._in_packet.packet)
        mid = mid[0]
        self._easy_log(MOSQ_LOG_DEBUG, "Received PUBREC (Mid: "+str(mid)+")")
        
        for i in range(len(self._messages)):
            if self._messages[i].direction == mosq_md_out and self._messages[i].mid == mid:
                self._messages[i].state = mosq_ms_wait_pubcomp
                self._messages[i].timestamp = time.time()
                return self._send_pubrel(mid, False)
        
        return MOSQ_ERR_SUCCESS

    def _handle_unsuback(self):
        if self._strict_protocol:
            if self._in_packet.remaining_length != 2:
                return MOSQ_ERR_PROTOCOL
        
        mid = struct.unpack("!H", self._in_packet.packet)
        mid = mid[0]
        self._easy_log(MOSQ_LOG_DEBUG, "Received UNSUBACK (Mid: "+str(mid)+")")
        self._callback_mutex.acquire()
        if self.on_unsubscribe:
            self._in_callback = True
            self.on_unsubscribe(self, self._obj, mid)
            self._in_callback = False
        self._callback_mutex.release()
        return MOSQ_ERR_SUCCESS

    def _handle_pubackcomp(self, cmd):
        if self._strict_protocol:
            if self._in_packet.remaining_length != 2:
                return MOSQ_ERR_PROTOCOL
        
        mid = struct.unpack("!H", self._in_packet.packet)
        mid = mid[0]
        self._easy_log(MOSQ_LOG_DEBUG, "Received "+cmd+" (Mid: "+str(mid)+")")
        
        for i in range(len(self._messages)):
            if self._messages[i].direction == mosq_md_out and self._messages[i].mid == mid:
                # Only inform the client the message has been sent once.
                self._callback_mutex.acquire()
                if self.on_publish:
                    self._in_callback = True
                    self.on_publish(self, self._obj, mid)
                    self._in_callback = False

                self._callback_mutex.release()
                self._messages.pop(i)

        return MOSQ_ERR_SUCCESS

    def _thread_main(self):
        run = True
        self._thread_terminate = False
        self._state_mutex.acquire()
        if self._state == mosq_cs_connect_async:
            self._state_mutex.release()
            self.reconnect()
        else:
            self._state_mutex.release()

        while run == True:
            rc = MOSQ_ERR_SUCCESS
            while rc == MOSQ_ERR_SUCCESS:
                rc = self.loop()
                if self._thread_terminate == True:
                    rc = 1
                    run = False

            self._state_mutex.acquire()
            if self._state == mosq_cs_disconnecting:
                run = False
                self._state_mutex.release()
            else:
                self._state_mutex.release()
                time.sleep(1)
                self.reconnect()

