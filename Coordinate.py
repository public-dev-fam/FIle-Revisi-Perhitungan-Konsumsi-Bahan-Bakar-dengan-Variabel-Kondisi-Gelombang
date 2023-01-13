#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import numpy as np
import geopy.distance
import ship

def Coordinate(nama_excel):
    pd.options.display.precision = 3
    data = pd.read_excel(nama_excel, usecols=[1,2])
    df = pd.DataFrame(data)
    df.columns = ['Lat1', 'Lng1']
    return df

def distance_route(jalur_pelayaran):
    route = Coordinate(jalur_pelayaran)
    new_route = route.copy()
    lat2 = new_route['Lat1']
    lat2 = lat2.drop(labels=[0], axis=0)
    lat2.loc[len(lat2.index)+1] = np.NaN
    lat2 = lat2.reset_index(drop=True)
    lon2 = new_route['Lng1']
    lon2 = lon2.drop(labels=[0], axis=0)
    lon2.loc[len(lon2.index)+1] = np.NaN
    lon2 = lon2.reset_index(drop=True)
    new_route.insert(2, 'Lat2', lat2)
    new_route.insert(3, 'Lng2', lon2)
    new_route = new_route.drop(labels=[len(route)-1])
    
    new_list = []
    for x in range(0, len(route)-1):
        coordinate = 'coordinate {}'.format(str(x))
        new_list.append(coordinate)    
    new_route.insert(0, "coordinate", new_list, True)          
    new_route['Distance (nm)'] = new_route.apply(lambda row : 
        distance(row['Lat1'], row['Lng1'], 
                 row['Lat2'], row['Lng2']
                ), axis=1)
    return new_route

def distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    estimate = geopy.distance.geodesic(coords_1, coords_2).nm
    return estimate

