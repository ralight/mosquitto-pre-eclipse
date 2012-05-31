/* Mosquitto MQTT Javascript/Websocket client */

function Mosquitto(url, keepalive)
{
	this.url = url;
	this.keepalive = keepalive;

	this.ws = new WebSocket(url, '[mqtt]');
	this.ws.binaryType = "blob";

	this.ws.onopen = function(evt) {
		var buffer = new ArrayBuffer(1+1+12+2+5);
		var int8View = new Int8Array(buffer);

		int8View[0] = 0x10;
		int8View[1] = 12+2+5;
		int8View[2] = 0;
		int8View[3] = 6;
		str = "MQIsdp";
		int8View[4] = str.charCodeAt(0);
		int8View[5] = str.charCodeAt(1);
		int8View[6] = str.charCodeAt(2);
		int8View[7] = str.charCodeAt(3);
		int8View[8] = str.charCodeAt(4);
		int8View[9] = str.charCodeAt(5);
		int8View[10] = 3;
		int8View[11] = 2;
		int8View[12] = 0;
		int8View[13] = 60;
		int8View[14] = 0;
		int8View[15] = 5;
		str = "roger";
		int8View[16] = str.charCodeAt(0);
		int8View[17] = str.charCodeAt(1);
		int8View[18] = str.charCodeAt(2);
		int8View[19] = str.charCodeAt(3);
		int8View[20] = str.charCodeAt(4);

		this.send(buffer);
	};

	this.ws.onclose = function(evt) {
	};

	this.ws.onmessage = function(evt) {
	};
}

Mosquitto.prototype.pub = function(message, qos, retain)
{
};

Mosquitto.prototype.pub = function(topic, qos)
{
};

