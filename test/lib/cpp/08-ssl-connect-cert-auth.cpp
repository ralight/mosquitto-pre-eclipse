#include <mosquittopp.h>

static int run = -1;

class mosquittopp_test : public mosqpp::mosquittopp
{
	public:
		mosquittopp_test(const char *id);

		void on_connect(int rc);
		void on_disconnect(int rc);
};

mosquittopp_test::mosquittopp_test(const char *id) : mosqpp::mosquittopp(id)
{
}

void mosquittopp_test::on_connect(int rc)
{
	if(rc){
		exit(1);
	}else{
		disconnect();
	}
}

void mosquittopp_test::on_disconnect(int rc)
{
	run = rc;
}


int main(int argc, char *argv[])
{
	struct mosquittopp_test *mosq;

	mosqpp::lib_init();

	mosq = new mosquittopp_test("08-ssl-connect-crt-auth");

	mosq->ssl_set("../ssl/test-ca.crt", NULL, "../ssl/client.crt", "../ssl/client.key");
	mosq->connect("localhost", 1888, 60);

	while(run == -1){
		mosq->loop();
	}

	mosqpp::lib_cleanup();

	return run;
}
