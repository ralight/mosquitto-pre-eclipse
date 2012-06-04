/* Mosquitto MQTT Javascript/Websocket client */

function AB2S(buffer) {
	var binary = '';
	var bytes = new Uint8Array(buffer);
	var len = bytes.byteLength;
	for(var i=0; i<len; i++){
		binary += String.fromCharCode(bytes[i]);
	}
	return binary;
}

function Mosquitto()
{
	this.ws = null;
}

Mosquitto.prototype = {
	mqtt_ping : function()
	{
		var buffer = new ArrayBuffer(2);
		var i8V = new Int8Array(buffer);
		i8V[0] = 0xC0;
		i8V[1] = 0;
		if(this.ws.readyState == 1){
			this.ws.send(buffer);
		}else{
			this.queue(buffer);
		}
		setTimeout(function(_this){_this.mqtt_ping();}, 60000, this);
	},

	connect : function(url, keepalive){

		this.url = url;
		this.keepalive = keepalive;
		this.mid = 1;
		this.out_queue = new Array();

		this.ws = new WebSocket(url, '[mqtt]');
		this.ws.binaryType = "arraybuffer";
		this.ws.onopen = this.ws_onopen;
		this.ws.onclose = this.ws_onclose;
		this.ws.onmessage = this.ws_onmessage;
		this.ws.m = this;
		this.ws.onerror = function(evt){
			alert(evt.data);
		}
	},

	disconnect : function(){
		if(this.ws.readyState == 1){
			var buffer = new ArrayBuffer(2);
			var i8V = new Int8Array(buffer);

			i8V[0] = 0xC0;
			i8V[1] = 0;
			this.ws.send(buffer);
			this.ws.close();
		}
	},

	ws_onopen : function(evt) {
		var buffer = new ArrayBuffer(1+1+12+2+20);
		var i8V = new Int8Array(buffer);

		i=0;
		i8V[i++] = 0x10;
		i8V[i++] = 12+2+20;
		i8V[i++] = 0;
		i8V[i++] = 6;
		str = "MQIsdp";
		for(var j=0; j<str.length; j++){
			i8V[i++] = str.charCodeAt(j);
		}
		i8V[i++] = 3;
		i8V[i++] = 2;
		i8V[i++] = 0;
		i8V[i++] = 60;
		i8V[i++] = 0;
		i8V[i++] = 20;
		var str = "mjsws/";
		for(var j=0; j<str.length; j++){
			i8V[i++] = str.charCodeAt(j);
		}
		var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
		for(var j=0; j<14; j++){
			i8V[i++] = chars.charCodeAt(Math.floor(Math.random()*chars.length));
		}

		this.send(buffer);
		while(this.m.out_queue.length > 0){
			this.send(this.m.out_queue.pop());
		}
		setTimeout(function(_this){_this.mqtt_ping();}, 60000, this.m);
	},

	ws_onclose : function(evt) {
		var p = document.createElement("p");
		p.innerHTML += "Lost connection";
		$("#debug").append(p);
	},

	ws_onmessage : function(evt) {
		var i8V = new Int8Array(evt.data);
		buffer = evt.data;
		var q=0;
		var p = document.createElement("p");
		while(i8V.length > 0 && q < 1000){
			q++;
			switch(i8V[0] & 0xF0){
				case 0x20:
					p.innerHTML += "CONNACK<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0x30:
					var i=1;
					var mult = 1;
					var rl = 0;
					var count = 0;
					var digit;
					do{
						count++;
						digit = i8V[i++];
						rl += (digit & 127)*mult;
						mult *= 128;
					}while((digit & 128) != 0);

					var topiclen = i8V[i++]*256 + i8V[i++];
					var atopic = buffer.slice(i, i+topiclen);
					i+=topiclen;
					var topic = AB2S(atopic);
					var apayload = buffer.slice(i, rl+count+1);
					var payload = AB2S(apayload);

					//p.innerHTML += "PUBLISH " + " " + topic + " " + (4+topiclen+1)+","+rl +" ." + payload +". ("+i8V.length+")";
					p.innerHTML += "PUBLISH " + topic + " "+payload+"<br>";
					buffer = buffer.slice(rl+1+count);
					i8V = new Int8Array(buffer);
					//p.innerHTML += " (nl "+i8V.length+" q:"+q+")<br>";

					break;
				case 0x40:
					p.innerHTML += "PUBACK<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0x50:
					p.innerHTML += "PUBREC<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0x60:
					p.innerHTML += "PUBREL<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0x70:
					p.innerHTML += "PUBCOMP<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0x80:
					p.innerHTML += "SUBSCRIBE  ("+i8V.length+")<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0x90:
					p.innerHTML += "SUBACK  ("+i8V.length+")<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0xA0:
					p.innerHTML += "UNSUBSCRIBE<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0xB0:
					p.innerHTML += "UNSUBACK<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0xC0:
					p.innerHTML += "PINGREQ<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0xD0:
					p.innerHTML += "PINGRESP<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				case 0xE0:
					p.innerHTML += "DISCONNECT<br>";
					var rl = i8V[1];
					buffer = buffer.slice(rl+2);
					i8V = new Int8Array(buffer);
					break;
				default:
					p.innerHTML += "Unknown command<br>";
					break;
			}
		}
		$("#debug").append(p);
	},

	get_remaining_count : function(remaining_length)
	{
		if(remaining_length >= 0 && remaining_length < 128){
			return 1;
		}else if(remaining_length >= 128 && remaining_length < 16384){
			return 2;
		}else if(remaining_length >= 16384 && remaining_length < 2097152){
			return 3;
		}else if(remaining_length >= 2097152 && remaining_length < 268435456){
			return 4;
		}else{
			return -1;
		}
	},

	queue : function(buffer)
	{
		this.out_queue.push(buffer);
	},

	unsubscribe : function(topic)
	{
		var rl = 2+2+topic.length;
		var remaining_count = this.get_remaining_count(rl);
		var buffer = new ArrayBuffer(1+remaining_count+rl);
		var i8V = new Int8Array(buffer);

		var i=0;
		i8V[i++] = 0xA2;
		do{
			digit = Math.floor(rl % 128);
			rl = Math.floor(rl / 128);
			if(rl > 0){
				digit = digit | 0x80;
			}
			i8V[i++] = digit;
		}while(rl > 0);
		i8V[i++] = 0;
		i8V[i++] = this.mid;
		this.mid++;
		if(this.mid == 256) this.mid = 0;
		i8V[i++] = 0;
		i8V[i++] = topic.length;
		for(var j=0; j<topic.length; j++){
			i8V[i++] = topic.charCodeAt(j);
		}

		if(this.ws.readyState == 1){
			this.ws.send(buffer);
		}else{
			this.queue(buffer);
		}
	},

	subscribe : function(topic, qos)
	{
		var rl = 2+2+topic.length+1;
		var remaining_count = this.get_remaining_count(rl);
		var buffer = new ArrayBuffer(1+remaining_count+rl);
		var i8V = new Int8Array(buffer);

		var i=0;
		i8V[i++] = 0x82;
		do{
			digit = Math.floor(rl % 128);
			rl = Math.floor(rl / 128);
			if(rl > 0){
				digit = digit | 0x80;
			}
			i8V[i++] = digit;
		}while(rl > 0);
		i8V[i++] = 0;
		i8V[i++] = this.mid;
		this.mid++;
		if(this.mid == 256) this.mid = 0;
		i8V[i++] = 0;
		i8V[i++] = topic.length;
		for(var j=0; j<topic.length; j++){
			i8V[i++] = topic.charCodeAt(j);
		}
		i8V[i++] = qos;

		if(this.ws.readyState == 1){
			this.ws.send(buffer);
		}else{
			this.queue(buffer);
		}
	},

	publish : function(topic, payload, qos){
		var rl = 2+2+topic.length+1;
		var remaining_count = this.get_remaining_count(rl);
		var buffer = new ArrayBuffer(1+remaining_count+rl);
		var i8V = new Int8Array(buffer);

		alert(rl);
		var i=0;
		i8V[i++] = 0x30;
		do{
			digit = Math.floor(rl % 128);
			rl = Math.floor(rl / 128);
			if(rl > 0){
				digit = digit | 0x80;
			}
			i8V[i++] = digit;
		}while(rl > 0);
		i8V[i++] = 0;
		i8V[i++] = topic.length;
		for(var j=0; j<topic.length; j++){
			i8V[i++] = topic.charCodeAt(j);
		}
		for(var j=0; j<payload.length; j++){
			i8V[i++] = payload.charCodeAt(j);
		}

		if(this.ws.readyState == 1){
			this.ws.send(buffer);
		}else{
			this.queue(buffer);
		}
	}
}

