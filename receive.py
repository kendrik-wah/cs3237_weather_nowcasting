from keras.models import load_model
from tensorflow.python.keras.backend import set_session
from PIL import Image
from os import listdir
from os.path import join

import tensorflow as tf
import paho.mqtt.client as mqtt
import numpy as np
import json


def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Successfully connected to broker.")
		client.subscribe("Group_B2/IMAGE/classify")
	else:
		print("Connection failed with code: %d." % rc)

def on_message(client, userdata, msg):
	recv_dict = json.loads(msg.payload)

	img_data = np.array(recv_dict["data"])
	result = classify_flower(recv_dict["filename"], img_data)

	print("Sending results: ", result)
	client.publish("Group_B2/IMAGE/predict", json.dumps(result))

def setup(hostname):
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(hostname)
	client.loop_start()
	return client

def main():
	setup("192.168.162.211")
	while True:
		pass

if __name__  == '__main__':
	main()
