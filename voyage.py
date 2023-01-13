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

def wave_list(data_coordinate_excel, ###dataframe untuk tabel
              data_set_gelombang, ##data hasil mendapatkan perhitungan gelombang
              data_kapal, ##data kapal
              start_time): ##waktu mulai
    route = Coordinate.distance_route(data_coordinate_excel)
    data2 = ship.particular(data_kapal)[1]['Value']
    initial_speed = data2[9]
    Lpp = data2[5]
    time = start_time
    list_height = []
    list_period = []
    list_direction = []
    speed_list = []
    time_list = []
    for coor, lat, lng, dist in zip(route['coordinate'],
                                    route['Lat1'], 
                                    route['Lng1'], 
                                    route['Distance (nm)'] 
                                    ):
        
        list_height.append(wave_data(str(lat), 
                                     str(lng), 
                                     time,
                                     coor,
                                     data_set_gelombang
                                    )[0]
                          )
        list_direction.append(wave_data(str(lat), 
                                     str(lng), 
                                     time,
                                     coor,
                                     data_set_gelombang
                                    )[1]
                          )
        list_period.append(wave_data(str(lat), 
                                     str(lng), 
                                     time,
                                     coor,
                                     data_set_gelombang
                                    )[2]
                          )
        
        speed_list.append(real_speed(list_height[len(list_height)-1],
                                        initial_speed, 
                                        Lpp
                                       )
                         )
        
        time_list.append(sail_time(dist,
                                   speed_list[len(speed_list)-1]))
        
        time = time + int(time_list[len(time_list)-1])
        
    return list_height, speed_list, time_list, list_direction, list_period

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
    data1 = Coordinate.distance_route(jalur_pelayaran)
    new_route = data1.copy()
    data2 = ship.particular(data_kapal)[1]['Value']
    initial_speed = data2[9]
    Lpp = data2[5]
    new_route['Initial speed (knot)'] = new_route.apply(lambda row : 
        initial_speed, axis=1)
    new_route['time 0 (hour)'] = new_route.apply(lambda row: 
        sail_time(row['Distance (nm)'], row['Initial speed (knot)']), axis=1)
    a = new_route['time 0 (hour)'].sum()
    list1 = [a]
    for x in new_route['time 0 (hour)']:
        if x != new_route['time 0 (hour)'][len(new_route['time 0 (hour)'])-1]:
            a = a - x
            list1.append(a)
    new_route['waktu kumulatif 0'] = pd.DataFrame(list1)
    data_gelombang = wave_list(data_coordinate_excel = jalur_pelayaran, 
                               data_set_gelombang = data_set_gelombang, 
                               data_kapal = data_kapal,
                               start_time = start_time)
    new_route['wave height (m)'] = pd.DataFrame(data_gelombang[0])
    new_route['wave direction'] = pd.DataFrame(data_gelombang[3])
    new_route['wave period'] = pd.DataFrame(data_gelombang[4])
    new_route['ship angle'] = new_route.apply(lambda row: 
        Geodesic.WGS84.Inverse(row['Lat1'], row['Lng1'], row['Lat2'], row['Lng2'])['azi1'], axis=1)
    new_route['heading angle'] = new_route.apply(lambda row: 
        (row['wave direction'] - row['ship angle']), axis=1)
    new_route['speed 1 (knot)'] = new_route.apply(lambda row: 
        real_speed(row['wave height (m)'], initial_speed, Lpp), axis=1)
    new_route['time 1 (hour)'] = new_route.apply(lambda row: 
        sail_time(row['Distance (nm)'], row['speed 1 (knot)']), axis=1)
    new_route['selisih 1-0'] = new_route.apply(lambda row: 
        (row['time 1 (hour)'] - row['time 0 (hour)']), axis=1)
    list2 = calc_time_selisih(new_route['time 1 (hour)'], new_route['selisih 1-0'])
    new_route['time 1 - (selisih 1-0)'] = pd.DataFrame(list2)
    b = new_route['time 1 - (selisih 1-0)'].sum()
    list3 = [b]
    for x in new_route['time 1 - (selisih 1-0)']:
        if x != new_route['time 1 - (selisih 1-0)'][len(new_route['time 1 - (selisih 1-0)'])-1]:
            b = b - x
            list3.append(b)
    new_route['waktu kumulatif 1'] = pd.DataFrame(list3)
    new_route['waktu kumulatif (1-0)'] = new_route.apply(lambda row: 
        (row['waktu kumulatif 1'] - row['waktu kumulatif 0']), axis=1)
    new_route['speed 2 (knot)'] = new_route.apply(lambda row: 
        (row['Distance (nm)'] / row['time 1 - (selisih 1-0)']), axis=1)
    list4 = []
    for x in new_route['speed 2 (knot)']:
        if x >= 18:
            list4.append(18)
        else:
            list4.append(x)
    new_route['speed setelah revisi'] = pd.DataFrame(list4)
    new_route['Distance 2 (nm)'] = new_route.apply(lambda row: 
        (row['speed setelah revisi'] * row['time 1 (hour)']), axis=1)
    new_route['koreksi distance'] = new_route.apply(lambda row: 
        (row['Distance (nm)'] - row['Distance 2 (nm)']), axis=1)
    list5 = calc_koreksi_distance(new_route['Distance 2 (nm)'], new_route['koreksi distance'])
    new_route['Distance 2 - koreksi'] = pd.DataFrame(list5)
    new_route['tambahan waktu yang dibutuhkan'] = new_route.apply(lambda row: 
        (row['koreksi distance'] / row['speed 2 (knot)']), axis=1)
    list560 = new_route['tambahan waktu yang dibutuhkan'].to_list()
    list561 = new_route['waktu kumulatif (1-0)'].to_list()
    list560_new = list560[1:]
    list560_new.append(0)
    list562 = []
    for x,y in zip(list560_new, list560):
        list562.append(x+y)        
    new_route['waktu kumulatif (1-0)'] = pd.DataFrame(list562)
    new_route['time 3 (hour)'] = new_route.apply(lambda row: 
        sail_time(row['Distance 2 - koreksi'], row['speed setelah revisi']), axis=1)
    new_route['selisih 3-0'] = new_route.apply(lambda row: 
        (row['time 3 (hour)'] - row['time 0 (hour)']), axis=1)
    list6 = calc_time_selisih(new_route['time 3 (hour)'], new_route['selisih 3-0'])
    new_route['time 3 - (selisih 3-0)'] = pd.DataFrame(list6)
    c = new_route['time 3 - (selisih 3-0)'].sum()
    list7 = [c]
    for x in new_route['time 3 - (selisih 3-0)']:
        if x != new_route['time 3 - (selisih 3-0)'][len(new_route['time 3 - (selisih 3-0)'])-1]:
            c = c - x
            list7.append(c)
    new_route['waktu kumulatif final'] = pd.DataFrame(list7)
    new_route['speed final (knot)'] = new_route.apply(lambda row: 
        (row['Distance 2 - koreksi'] / row['time 3 - (selisih 3-0)']), axis=1)
    return new_route

def Calculation(data_kapal, jalur_pelayaran, 
                data_set_gelombang, start_time):
    sfoc = ship.particular(data_kapal)[1]['Value'][14]
    df = Calculate(data_kapal, jalur_pelayaran, 
                   data_set_gelombang, start_time)
    
    data = Coordinate.distance_route(jalur_pelayaran).copy()
    data['wave height (m)'] = df['wave height (m)']
    data['wave period'] = df['wave period']
    data['wave direction'] = df['wave direction']
    data['heading angle'] = df['heading angle']
    data['speed final (knot)'] = df['speed final (knot)']
    data['time (hour)'] = df['time 3 (hour)']
    data['R Calm Water (kN)'] = data.apply(lambda row: 
        ship.resistance_calm_water(row['speed final (knot)'], data_kapal), axis=1)
    data['R Added Wave (kN)'] = data.apply(lambda row: 
        RAW.Calculation(data_kapal, row['wave height (m)'], row['wave period'],
                       row['heading angle'], row['speed final (knot)'] ), axis=1)
    data['R Total (kN)'] = data.apply(lambda row: 
        (row['R Calm Water (kN)'] + row['R Added Wave (kN)']), axis=1)    
    data['Power (kwh)'] = data.apply(lambda row: 
        ship.power(row['speed final (knot)'], row['R Calm Water (kN)'], row['R Added Wave (kN)'],
                       data_kapal), axis=1)
    data['foc (ton)'] = data.apply(lambda row: 
        foc(row['speed final (knot)'], row['Power (kwh)'], sfoc), axis=1)
    return data

def Calculation(data_kapal, jalur_pelayaran, 
                data_set_gelombang, start_time):
    sfoc = ship.particular(data_kapal)[1]['Value'][14]
    df = Calculate(data_kapal, jalur_pelayaran, 
                   data_set_gelombang, start_time)
    
    data = Coordinate.distance_route(jalur_pelayaran).copy()
    data['wave height (m)'] = df['wave height (m)']
    data['wave period'] = df['wave period']
    data['wave direction'] = df['wave direction']
    data['heading angle'] = df['heading angle']
    data['speed final (knot)'] = df['speed final (knot)']
    data['time (hour)'] = df['time 3 (hour)']
    data['R Calm Water (kN)'] = data.apply(lambda row: 
        ship.resistance_calm_water(row['speed final (knot)'], data_kapal), axis=1)
    data['R Added Wave (kN)'] = data.apply(lambda row: 
        RAW.Calculation(data_kapal, row['wave height (m)'], row['wave period'],
                       row['heading angle'], row['speed final (knot)'] ), axis=1)
    data['R Total (kN)'] = data.apply(lambda row: 
        (row['R Calm Water (kN)'] + row['R Added Wave (kN)']), axis=1)    
    data['Power (kwh)'] = data.apply(lambda row: 
        ship.power(row['speed final (knot)'], row['R Calm Water (kN)'], row['R Added Wave (kN)'],
                       data_kapal), axis=1)
    data['foc (ton)'] = data.apply(lambda row: 
        foc(row['time (hour)'], row['Power (kwh)'], sfoc), axis=1)
    return data

def Perbandingan(jalur_pelayaran, data_kapal):
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
        ship.power(row['speed (knot)'], row['R Calm Water (kN)'], 0,
                       data_kapal), axis=1)
    new_route['foc (ton)'] = new_route.apply(lambda row: 
        foc(row['time (hour)'], row['Power (kwh)'], sfoc), axis=1)
    return new_route
