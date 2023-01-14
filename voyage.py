#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import Vs_decision
import Coordinate
import ship
import RAW
from geographiclib.geodesic import Geodesic

def wave_data(lng, lat, time, coordinate, data_set_gelombang):
    data = pd.read_excel(data_set_gelombang)
    string1 = '{} Wave Height'.format(coordinate)
    string2 = '{} Wave Direction'.format(coordinate)
    string3 = '{} Wave Period'.format(coordinate)
    wave_height = data[string1][time]
    wave_direction = data[string2][time]
    wave_period = data[string3][time]
    return wave_height, wave_direction, wave_period

def data_processing_from_coordinate(data_coordinate_excel,  ###dataframe untuk tabel
                                    data_set_gelombang,  ##data hasil mendapatkan perhitungan gelombang
                                    data_kapal,  ##data kapal
                                    start_time): ##waktu mulai
    route = Coordinate.distance_route(data_coordinate_excel)
    ship_particular = ship.particular(data_kapal)[0]['Value']
    initial_speed = ship_particular[0]
    Lpp = ship_particular[3]
    sfoc = ship_particular[15]
    BHP = ship_particular[13]
    time = start_time
    list_wave_height = []
    list_wave_period = []
    list_wave_direction = []
    list_speed = []
    list_time = []
    list_ship_angle = []
    list_heading_angle = []
    list_resistance_calm_water = []
    list_resistance_added_wave = []
    list_resistance_total = []
    list_power = []
    list_foc = []
    for coor, lat1, lng1, lat2, lng2, dist in zip(
                                    route['coordinate'],
                                    route['Lat1'], 
                                    route['Lng1'],
                                    route['Lat2'],
                                    route['Lng2'],
                                    route['Distance (nm)'] 
                                    ):
        extract_wave_data = wave_data(str(lat1), str(lng1), time, coor, data_set_gelombang)
        temp_height = extract_wave_data[0]
        temp_wave_direction = extract_wave_data[1]
        temp_wave_period = extract_wave_data[2]
        temp_speed = real_speed(list_wave_height[len(list_wave_height)-1],
                                        initial_speed, Lpp
        temp_time =
        list_wave_height.append(extract_wave_data[0])
        list_wave_direction.append(extract_wave_data[1])
        list_wave_period.append(extract_wave_data[2])
        list_speed.append(real_speed(list_wave_height[len(list_wave_height)-1],
                                        initial_speed, 
                                        Lpp
                                       )
                         )
        list_time.append(sail_time(
            dist,list_speed[len(list_speed)-1]
                                   ))
        time = time + round(list_time[len(list_time)-1])
        list_ship_angle.append(Geodesic.WGS84.Inverse(
            lat1, lng1, lat2, lng2)['azi1'])
        list_heading_angle.append((list_wave_direction[len(list_wave_direction)-1]) - (
            list_ship_angle[len(list_ship_angle)-1]))
        list_resistance_calm_water.append(ship.resistance_calm_water(
            list_speed[len(list_speed)-1], data_kapal
        ))
        list_resistance_added_wave.append(RAW.Calculation(
            data_kapal, list_wave_height[len(list_wave_height)-1],
            list_wave_period[len(list_wave_period)-1],
            list_heading_angle[len(list_heading_angle)-1],
            list_speed[len(list_speed)-1]
        ))
        list_resistance_total.append(
            list_resistance_calm_water[len(list_resistance_calm_water)-1] + list_resistance_added_wave[
                len(list_resistance_added_wave)-1]
        )
        list_power.append(ship.power(
            list_speed[len(list_speed)-1],
            list_resistance_total[len(list_resistance_total)-1],
            data_kapal
        ))
        list_foc.append(foc(
            list_time[len(list_time)-1],
            list_power[len(list_power)-1],
            sfoc
        ))
    return (list_wave_height, list_speed, list_time,
            list_wave_direction, list_wave_period,
            list_ship_angle, list_heading_angle,
            list_resistance_calm_water, list_resistance_added_wave,
            list_resistance_total, list_power, list_foc)

def round_one(number):
    value = float("{0:.1f}".format(number))
    return value

def real_speed(wave_height, speed, Lpp):
    data = Vs_decision.support_decision(Lpp, speed)[1]
    for x,y,z in zip(data[0], data[1], data[2]):
        if x < wave_height and wave_height < y:
            speed_initial = z
            speed_initial = str(round(speed_initial, 3))
            speed_initial = float(speed_initial)
            break
        else:
            speed_initial = 'error'
    return speed_initial

def sail_time(distance, speed):
    knot = 0.514 #m/s
    nm = 1.852 #km    
    second = distance*nm*1000/(speed*knot) #time in second
    minute = second/60 #time in minute
    hour = minute/60 #time in hour
    return hour

def foc(time, BHP, sfoc):
    fuel = time*sfoc*BHP
    fuel_ton = fuel/(10**6)
    return fuel_ton

def calc_time_selisih(data1, data2):
    ts = [] ##time-selisih
    ts.append(data1[0])
    for x,y in zip(data1[1:], data2):
        ts.append(x-y)
    ts[len(ts)-1] = ts[len(ts)-1] - data2[len(data2)-1]
    return ts

def calc_koreksi_distance(data1, data2):
    ts = [] ##time-selisih
    ts.append(data1[0])
    for x,y in zip(data1[1:], data2):
        ts.append(x+y)
    ts[len(ts)-1] = ts[len(ts)-1] + data2[len(data2)-1]
    return ts

def Calculate(data_kapal, jalur_pelayaran, data_set_gelombang, start_time):
    lat_lng_data = Coordinate.distance_route(jalur_pelayaran)
    calculation = lat_lng_data.copy()
    load_data = data_processing_from_coordinate(data_coordinate_excel = jalur_pelayaran,
                                                data_set_gelombang = data_set_gelombang,
                                                data_kapal = data_kapal,
                                                start_time = start_time)
    #Load_data result(list_wave_height#0, speed_list#1, time_list#2, list_wave_direction#3,
    # list_wave_period#4, list_ship_angle#5, list_heading_angle#6)
    #list_resistance_calm_water#7, list_resistance_added_wave#8,
    # list_resistance_total#9, list_power#10, list_foc#11)
    calculation['wave height (m)'] = pd.DataFrame(load_data[0])
    calculation['wave direction'] = pd.DataFrame(load_data[3])
    calculation['wave period'] = pd.DataFrame(load_data[4])
    calculation['ship angle'] = pd.DataFrame(load_data[5])
    calculation['heading angle'] = pd.DataFrame(load_data[6])
    calculation['speed (knot)'] = pd.DataFrame(load_data[1])
    calculation['time (hour)'] = pd.DataFrame(load_data[2])
    calculation['R Calm Water (kN)'] = pd.DataFrame(load_data[7])
    calculation['R Added Wave (kN)'] = pd.DataFrame(load_data[8])
    calculation['R Total (kN)'] = pd.DataFrame(load_data[9])
    calculation['Power (kwh)'] = pd.DataFrame(load_data[10])
    calculation['foc (ton)'] = pd.DataFrame(load_data[11])
    return calculation

def foc_in_calm_water(jalur_pelayaran, data_kapal):
    data1 = Coordinate.distance_route(jalur_pelayaran)
    sfoc = ship.particular(data_kapal)[1]['Value'][14]
    new_route = data1.copy()
    data2 = ship.particular(data_kapal)[1]['Value']
    initial_speed = data2[9]
    Lpp = data2[5]
    new_route['speed (knot)'] = new_route.apply(lambda row :
        initial_speed, axis=1)
    new_route['time (hour)'] = new_route.apply(lambda row: 
        sail_time(row['Distance (nm)'], row['speed (knot)']), axis=1)
    new_route['R Calm Water (kN)'] = new_route.apply(lambda row: 
        ship.resistance_calm_water(row['speed (knot)'], data_kapal), axis=1)
    new_route['Power (kwh)'] = new_route.apply(lambda row: 
        ship.power(row['speed (knot)'],
                   row['R Calm Water (kN)'],
                   data_kapal), axis=1)
    new_route['foc (ton)'] = new_route.apply(lambda row: 
        foc(row['time (hour)'], row['Power (kwh)'], sfoc), axis=1)
    return new_route
