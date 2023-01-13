#!/usr/bin/env python
# coding: utf-8

# In[6]:

import requests
import pandas as pd
import numpy as np
import csv
import Coordinate

url = "https://stormglass.p.rapidapi.com/forecast"
headers = {
	"X-RapidAPI-Key": "72c272f074mshdc71dabcdc6e89fp1138b1jsnda7d346a63ed",
	"X-RapidAPI-Host": "stormglass.p.rapidapi.com"
}

def wave_data(lat, lng):
    querystring = {"lng":lng,"lat":lat}
    response = requests.request("GET", url, headers=headers, params=querystring)
    result = response.json()
    list_data = []
    dict_waveheight = {}
    dict_wavedirection = {}
    dict_waveperiod = {}
    list_waveheight = []
    list_wavedirection = []
    list_waveperiod = []
    for value in result['hours']:
        if len(value['waveHeight']) > 0:
            for item in value['waveHeight']:
                if item['source'] == 'meteo':
                    list_waveheight.append(item['value'])
                    break
                elif item['source'] == 'icon':
                    list_waveheight.append(item['value'])
                    break
                elif item['source'] == 'sg':
                    list_waveheight.append(item['value'])
                    break
        else:
            list_waveheight.append(np.nan)
                
    for value in result['hours']:
        if len(value['waveDirection']) > 0:
            for item in value['waveDirection']:
                if item['source'] == 'meteo':
                    list_wavedirection.append(item['value'])
                    break
                elif item['source'] == 'icon':
                    list_wavedirection.append(item['value'])
                    break
                elif item['source'] == 'sg':
                    list_wavedirection.append(item['value'])
                    break
        else:
            list_wavedirection.append(np.nan)

                
    for value in result['hours']:
        if len(value['wavePeriod']) > 0:
            for item in value['wavePeriod']:
                if item['source'] == 'meteo':
                    list_waveperiod.append(item['value'])
                    break
                elif item['source'] == 'icon':
                    list_waveperiod.append(item['value'])
                    break
                elif item['source'] == 'sg':
                    list_waveperiod.append(item['value'])
                    break
        else:
            list_waveperiod.append(np.nan)      
                
    dict_waveheight['Wave Height'] = list_waveheight
    dict_wavedirection['Wave Direction'] =  list_wavedirection
    dict_waveperiod['Wave Period'] = list_waveperiod
    list_data.append(dict_waveheight)
    list_data.append(dict_wavedirection)
    list_data.append(dict_waveperiod)
    return list_data

def wavedata_list(nama_excel):
    route = Coordinate.distance_route(nama_excel)
    dict_coordinate = {}
    x = 0
    for latitude, longitude in zip(route['Lat1'], route['Lng1']):
        coordinate = 'coordinate {}'.format(str(x))
        data = wave_data(str(latitude), str(longitude))
        dict_coordinate[coordinate] = data
        x += 1
    return dict_coordinate

def save_excel(coordinate_data, nama_file):
    data = wavedata_list(coordinate_data)
    dict1 = {}
    for key, value in data.items():
        for item in value:
            for x,y in item.items():
                coordinate = '{} {}'.format(str(key), str(x))
                dict1[coordinate] = y
    df_data = pd.DataFrame.from_dict(dict1)
    
    df_data.to_excel(nama_file)
    return df_data
    
def save_csv(coordinate_data, nama_file):
    data = wavedata_list(coordinate_data)
    dict1 = {}
    for key, value in data.items():
        for item in value:
            for x,y in item.items():
                coordinate = '{} {}'.format(str(key), str(x))
                dict1[coordinate] = y
    df_data = pd.DataFrame.from_dict(dict1)
    
    df_data.to_csv(nama_file, encoding='utf-8')
    return df_data

