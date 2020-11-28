from wr_rain_pred import *
from lstm import*

import gc

from datetime import datetime
from dateutil import tz
import os


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
    
    if len(str(hour)) == 1:
        hour = '0' + str(hour)

    if len(str(minute)) == 1:
        minute = '0' + str(minute)

    time_now = year + "/" + month + "/" + day + "\t" + str(hour) + ":" + str(minute) + ":" + second

    return time_now


def main():
    try:
        is_rain_LSTM, pr_rain_LSTM = LSTM_get_rain_prediction()
        gc.collect()
        is_rain_CNN, pr_rain_CNN = CNN_get_rain_prediction(lead_time=4)
        gc.collect()

        print("\n\n\n\n")
        print("Predicted Time:", getTime())

        if is_rain_LSTM:
            print("LSTM -- Prediction: Rain with probability {}".format(pr_rain_LSTM))
        else:
            print("LSTM -- Prediction: No rain with probability {}".format(1 - pr_rain_LSTM))

        if is_rain_CNN:
            print("CNN -- Prediction: Rain with probability {}".format(pr_rain_CNN))
        else:
            print("CNN -- Prediction: No rain with probability {}".format(1-pr_rain_CNN))

        print("\n\n\n\n")
    

    except:
        print("ERROR")
        time.sleep(2)

if __name__  == '__main__':
    main()

