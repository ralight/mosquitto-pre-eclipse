import struct

def packet_matches(name, recvd, expected):
    if recvd != expected:
        print("FAIL: Received incorrect "+name+".")
        print("Received: "+to_string(recvd))
        print("Expected: "+to_string(expected))
        return 0
    else:
        return 1

def remaining_length(packet):
    l = min(5, len(packet))
    all_bytes = struct.unpack("!"+"B"*l, packet[:l])
    mult = 1
    rl = 0
    for i in range(1,l-1):
        byte = all_bytes[i]

        rl += (byte & 127) * mult
        mult *= 128
        if byte & 128 == 0:
            packet = packet[i+1:]
            break

    return (packet, rl)


def to_string(packet):
    if len(packet) == 0:
        return ""

    packet0 = struct.unpack("!B", packet[0])
    packet0 = packet0[0]
    cmd = packet0 & 0xF0
    if cmd == 0x00:
        # Reserved
        return "0x00"
    elif cmd == 0x10:
        # CONNECT
        (packet, rl) = remaining_length(packet)
        pack_format = "!H" + str(len(packet)-2) + 's'
        (slen, packet) = struct.unpack(pack_format, packet)
        pack_format = "!" + str(slen)+'sBBH' + str(len(packet)-slen-4) + 's'
        (protocol, proto_ver, flags, keepalive, packet) = struct.unpack(pack_format, packet)
        s = "CONNECT, proto="+protocol+str(proto_ver)+", keepalive="+str(keepalive)
        if flags&2:
            s = s+", clean-session"
        else:
            s = s+", durable"

        pack_format = "!H" + str(len(packet)-2) + 's'
        (slen, packet) = struct.unpack(pack_format, packet)
        pack_format = "!" + str(slen)+'s' + str(len(packet)-slen) + 's'
        (client_id, packet) = struct.unpack(pack_format, packet)
        s = s+", id="+client_id

        if flags&4:
            pack_format = "!H" + str(len(packet)-2) + 's'
            (slen, packet) = struct.unpack(pack_format, packet)
            pack_format = "!" + str(slen)+'s' + str(len(packet)-slen) + 's'
            (will_topic, packet) = struct.unpack(pack_format, packet)
            s = s+", will-topic="+will_topic

            pack_format = "!H" + str(len(packet)-2) + 's'
            (slen, packet) = struct.unpack(pack_format, packet)
            pack_format = "!" + str(slen)+'s' + str(len(packet)-slen) + 's'
            (will_message, packet) = struct.unpack(pack_format, packet)
            s = s+", will-message="+will_message

            s = s+", will-qos="+str((flags&24)>>3)
            s = s+", will-retain="+str((flags&32)>>5)

        if flags&128:
            pack_format = "!H" + str(len(packet)-2) + 's'
            (slen, packet) = struct.unpack(pack_format, packet)
            pack_format = "!" + str(slen)+'s' + str(len(packet)-slen) + 's'
            (username, packet) = struct.unpack(pack_format, packet)
            s = s+", username="+username

        if flags&64:
            pack_format = "!H" + str(len(packet)-2) + 's'
            (slen, packet) = struct.unpack(pack_format, packet)
            pack_format = "!" + str(slen)+'s' + str(len(packet)-slen) + 's'
            (password, packet) = struct.unpack(pack_format, packet)
            s = s+", password="+password

        return s
    elif cmd == 0x20:
        # CONNACK
        print(len(packet))
        (cmd, rl, resv, rc) = struct.unpack('!BBBB', packet)
        return "CONNACK, rl="+str(rl)+", res="+str(resv)+", rc="+str(rc)
    elif cmd == 0x30:
        # PUBLISH
        dup = (packet0 & 0x08)>>3
        qos = (packet0 & 0x06)>>1
        retain = (packet0 & 0x01)
        (packet, rl) = remaining_length(packet)
        pack_format = "!H" + str(len(packet)-2) + 's'
        (tlen, packet) = struct.unpack(pack_format, packet)
        pack_format = "!" + str(tlen)+'s' + str(len(packet)-tlen) + 's'
        (topic, packet) = struct.unpack(pack_format, packet)
        s = "PUBLISH, rl="+str(rl)+", qos="+str(qos)+", retain="+str(retain)+", dup="+str(dup)
        if qos > 0:
            pack_format = "!H" + str(len(packet)-2) + 's'
            (mid, packet) = struct.unpack(pack_format, packet)
            s = s + ", mid="+str(mid)

        s = s + ", payload="+packet
        return s
    elif cmd == 0x40:
        # PUBACK
        (cmd, rl, mid) = struct.unpack('!BBH', packet)
        return "PUBACK, rl="+str(rl)+", mid="+str(mid)
    elif cmd == 0x50:
        # PUBREC
        (cmd, rl, mid) = struct.unpack('!BBH', packet)
        return "PUBREC, rl="+str(rl)+", mid="+str(mid)
    elif cmd == 0x60:
        # PUBREL
        dup = (packet0 & 0x08)>>3
        (cmd, rl, mid) = struct.unpack('!BBH', packet)
        return "PUBREL, rl="+str(rl)+", mid="+str(mid)+", dup="+str(dup)
    elif cmd == 0x70:
        # PUBCOMP
        (cmd, rl, mid) = struct.unpack('!BBH', packet)
        return "PUBCOMP, rl="+str(rl)+", mid="+str(mid)
    elif cmd == 0x80:
        # SUBSCRIBE
        (packet, rl) = remaining_length(packet)
        pack_format = "!H" + str(len(packet)-2) + 's'
        (mid, packet) = struct.unpack(pack_format, packet)
        s = "SUBSCRIBE, rl="+str(rl)+", mid="+str(mid)
        topic_index = 0
        while len(packet) > 0:
            pack_format = "!H" + str(len(packet)-2) + 's'
            (tlen, packet) = struct.unpack(pack_format, packet)
            pack_format = "!" + str(tlen)+'sB' + str(len(packet)-tlen-1) + 's'
            (topic, qos, packet) = struct.unpack(pack_format, packet)
            s = s + ", topic"+str(topic_index)+"="+topic+","+str(qos)
        return s
    elif cmd == 0x90:
        # SUBACK
        (packet, rl) = remaining_length(packet)
        pack_format = "!H" + str(len(packet)-2) + 's'
        (mid, packet) = struct.unpack(pack_format, packet)
        pack_format = "!" + "B"*len(packet)
        granted_qos = struct.unpack(pack_format, packet)
        
        s = "SUBACK, rl="+str(rl)+", mid="+str(mid)+", granted_qos="+str(granted_qos[0])
        for i in range(1, len(granted_qos)-1):
            s = s+", "+str(granted_qos[i])
        return s
    elif cmd == 0xA0:
        # UNSUBSCRIBE
        (packet, rl) = remaining_length(packet)
        pack_format = "!H" + str(len(packet)-2) + 's'
        (mid, packet) = struct.unpack(pack_format, packet)
        s = "UNSUBSCRIBE, rl="+str(rl)+", mid="+str(mid)
        topic_index = 0
        while len(packet) > 0:
            pack_format = "!H" + str(len(packet)-2) + 's'
            (tlen, packet) = struct.unpack(pack_format, packet)
            pack_format = "!" + str(tlen)+'s' + str(len(packet)-tlen) + 's'
            (topic, packet) = struct.unpack(pack_format, packet)
            s = s + ", topic"+str(topic_index)+"="+topic
        return s
    elif cmd == 0xB0:
        # UNSUBACK
        (cmd, rl, mid) = struct.unpack('!BBH', packet)
        return "UNSUBACK, rl="+str(rl)+", mid="+str(mid)
    elif cmd == 0xC0:
        # PINGREQ
        (cmd, rl) = struct.unpack('!BB', packet)
        return "PINGREQ, rl="+str(rl)
    elif cmd == 0xD0:
        # PINGRESP
        (cmd, rl) = struct.unpack('!BB', packet)
        return "PINGRESP, rl="+str(rl)
    elif cmd == 0xE0:
        # DISCONNECT
        (cmd, rl) = struct.unpack('!BB', packet)
        return "DISCONNECT, rl="+str(rl)
    elif cmd == 0xF0:
        # Reserved
        return "0xF0"
