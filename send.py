import paho.mqtt.client as mqtt
import numpy as np
from PIL import Image
import json

from os import listdir
from os.path import join


def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected.")
		client.subscribe("weather/pred")
	else:
		print("Failed to connect. Error code: %d." % rc)

def on_message(client, userdata, msg):
	print("Received message from server.")
	msg_data = json.loads(msg.payload)
	print(msg_data)

def setup(hostname):
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(hostname)
	client.loop_start()
	return client

def send(client):
	client.publish("weather/main", json.dumps("request"))


def main():
    client = setup("localhost") # change this IP address. on your WSL, use 'ifconfig' to obtain your IP address.
    print("Sending data.")
    send(client)
    while True:
        pass

if __name__ == '__main__':
	main()
