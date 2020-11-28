from wr_rain_pred import *
from lstm import*

from datetime import datetime
from dateutil import tz

import paho.mqtt.client as mqtt
import json

def getTime():

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Singapore')

    utc = datetime.utcnow()

    # Change timezone from UTC to Singapore time
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    sg_time = utc.astimezone(to_zone)
    year = '2020'
    month = '11'
    day = str(sg_time.strftime("%d"))

    hour = int(sg_time.strftime("%H"))+1

    minute = int(sg_time.strftime("%M"))
    second = '0000'
    
    name = year + "/" + month + "/" + day + "\t" + str(hour) + ":" + str(minute) + ":" + second

    return name

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Successfully connected to broker.")
		client.subscribe("weather/main")
	else:
		print("Connection failed with code: %d." % rc)

def on_message(client, userdata, msg):

    msg_data = json.loads(msg.payload)

    if(len(msg_data) > 2):
        print(msg_data)
        result = "TEST"
        try:
            is_rain_LSTM, pr_rain_LSTM = LSTM_get_rain_prediction()
            is_rain_CNN, pr_rain_CNN = CNN_get_rain_prediction(lead_time=4)

            print("\n\n\n\n")
            print("Predicted Time:", getTime())
  
        
            if is_rain_LSTM:
                result = "RAIN"
                print("LSTM -- Prediction: Rain with probability: {}".format(pr_rain_LSTM))
            else:
                result = "NO RAIN"
                print("LSTM -- Prediction: No rain with probability: {}".format(1-pr_rain_LSTM))

            if is_rain_CNN:
                print("CNN -- Prediction: Rain with probability: {}".format(pr_rain_CNN))
            else:
                print("CNN -- Prediction: No rain with probability: {}".format(1-pr_rain_CNN))

            #if is_rain_CNN and is_rain_LSTM:
            #    print("Please rain")
             #   result = "Rain"
            #elif is_rain_CNN:
            #    print("Maybe no rain")
            #    result = "Maybe No Rain"
            #elif is_rain_LSTM:
            #    print("Maybe no rain")
            #    result = "Maybe Rain"
            #else:
            #    print("Definitely no rain")
            #    result = "No Rain"
            print("\n\n\n\n")
            client.publish("weather/pred", json.dumps(result))
            

        except:
            print("ERROR")
            time.sleep(2)
            print("Trying again")

	

def setup(hostname):
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(hostname)
	client.loop_start()
	return client

def main():
	setup("localhost")
	print("Server is online")
	while True:
		pass

if __name__  == '__main__':
	main()

