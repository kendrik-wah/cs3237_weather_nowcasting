from tensorflow.keras.models import load_model
import numpy as np
import requests
import time
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from sklearn.preprocessing import MinMaxScaler
import joblib


LSTM_MODEL_NAME='LSTMfiveVars.h5'
DENSENN_MODEL_NAME = 'rainbooleanfiveVars.h5'

"""Run LSTM and custom neural network to predict rain"""

def get_weather_api_data(appkey, lat, lon):

    payload = {'key': appkey,
              'q': str(lat) + ',' + str(lon)}

    responseJson = requests.get("http://api.weatherapi.com/v1/current.json", params=payload).json()

    result = {'date_time': responseJson['location']["localtime"],
             # 'day': bool(responseJson["current"]["is_day"]),
              'temp': responseJson["current"]["temp_c"],
              'humidity': responseJson["current"]["humidity"],
              'wind_speed': responseJson["current"]["wind_kph"],
              'uv_idx': responseJson["current"]["uv"],
              'visibility': responseJson["current"]["vis_km"],
              'ccover': responseJson["current"]["cloud"]/100,
              'pressure': responseJson["current"]["pressure_mb"],
              'is_rain': ((responseJson["current"]["condition"]['text']=='Light rain') or
                (responseJson["current"]["condition"]['text']=='Moderate or heavy rain with thunder') or
                (responseJson["current"]["condition"]['text']=='Moderate rain') or
                (responseJson["current"]["condition"]['text']=='Moderate rain at times') or
                (responseJson["current"]["condition"]['text']=='Patchy light rain with thunder') or
                (responseJson["current"]["condition"]['text']=='Patchy rain possible'))}

    return result


def reorg_data(result):
    result.pop('date_time')
    result.pop('is_rain')

#    if result['day'] is False:
#       result['day'] = 0
#    else:
#        result['day'] = 1

    new_order = [result['temp'], result['humidity']/100, result['wind_speed'],
                 result['uv_idx'], result['pressure']]
    
    #print(new_order)
    
    return np.array(new_order)


def get_latest_result():
    result = get_weather_api_data("use_your_own_app_key_dude", 1.3973, 103.7475)
    mongoClient = MongoClient('some_database_have_fun_figuring_this_out')
    mydb = mongoClient['sensortag']

    mycol = mydb['data']

    one_hour_result = mycol.find().sort([('$natural', -1)]).limit(1)

    for j in one_hour_result:
      result['temp'] = round(j['Ambient Temp'],1)
      result['pressure'] = round(j['Pressure'],1)
      result['humidity'] = round(j['Humidity'],1)

      result = reorg_data(result) 
    return result


def get_rain_prediction(LSTM_MODEL_NAME, DENSENN_MODEL_NAME, currThreeScaled):
    print("\n\nGenerating time series prediction using LSTM network...\n\n")
    LSTM_model = load_model(LSTM_MODEL_NAME)
    DenseNN_model = load_model(DENSENN_MODEL_NAME)
    intermediate_result = LSTM_model.predict(currThreeScaled)
    print("\n\nDone!\n\n")
    #print(intermediate_result)  # for debugging
    
    print("Predicting the probability of rain...")
    decision = DenseNN_model.predict(intermediate_result)

    pr_rain = decision[0][0]
    if decision[0][0] >= 0.5:
        is_rain = True
        #print("Prediction: rain with probability {}".format(decision[0][0]))
    else:
        is_rain = False
        #print("Prediction: no rain with probability {}".format(1- decision[0][0]))
    print("Done!\n\n")

    return is_rain, pr_rain


def LSTM_get_rain_prediction():
    
    print("\n\nCollecting the past 3 hours of SensorTag data from MongoDB...")
    mongoClient = MongoClient('some_database_have_fun_figuring_this_out')
    mydb = mongoClient['sensortag']
    mycol = mydb['data']
    three_hour_results = mycol.find().sort([('$natural', -1)]).limit(3)

    humidity = []
    pressure = []
    temp = []

    for j in three_hour_results:
        humidity.append(round(j['Humidity'],1))
        pressure.append(round(j['Pressure'],1))
        temp.append(round(j['Ambient Temp'],1))

    humidity.reverse()
    pressure.reverse()
    temp.reverse()
    print("Done!\n\n")


    # Collect 3 hours worth of data from Weather API
    prev = []
    for i in range(3):
       result = get_weather_api_data("use_your_own_app_key_dude", 1.3973, 103.7475)  # Get all the data from weather API (output: dict)
    
       result['temp'] = temp[i]
       result['pressure'] = pressure[i]
       result['humidity'] = humidity[i]
       #print(result)
       # overwrite sensortag values into the dict (TODO)
       result = reorg_data(result)  # re-organize the data 
       #print(result)
       prev.append(result)
       time.sleep(2) 

    latest = get_weather_api_data("use_your_own_app_key_dude", 1.3973, 103.7475)
    latest = reorg_data(latest)
    input_data = np.concatenate([prev, latest[np.newaxis, ::]], axis=0)

    currThree = np.expand_dims(input_data[:3], axis=0)

    currThreeScaled = []
    my_scaler = joblib.load('scaler1.pkl')
    for curr in currThree:
         currThreeScaled.append(my_scaler.transform(curr))

    currThreeScaled = np.array(currThreeScaled)

    # Use the LSTM and dense neural network to predict rain
    #get_rain_prediction(LSTM_MODEL_NAME, DENSENN_MODEL_NAME)

    is_rain, pr_rain = get_rain_prediction(LSTM_MODEL_NAME, DENSENN_MODEL_NAME, currThreeScaled)

    return is_rain, pr_rain 

#print(LSTM_get_rain_prediction())



