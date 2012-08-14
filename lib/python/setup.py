from sys import version

from distutils.core import setup
setup(name='mosquitto',
	version='1.0.1',
	description='MQTT version 3.1 client class',
	author='Roger Light',
	author_email='roger@atchoo.org',
	url='http://mosquitto.org/',
	download_url='http://mosquitto.org/files/',
	license='BSD License',
	py_modules=['mosquitto']
	)
