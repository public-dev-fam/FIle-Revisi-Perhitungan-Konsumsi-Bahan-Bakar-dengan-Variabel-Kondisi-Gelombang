#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np

def support_decision(Lpp, speed):
    min_wave = 0.02*Lpp
    max_wave = 0.04*Lpp
    perwaverange = [
        '0-50%', '50-55%', '55-60%', '60-65%', '65-70%',
        '70-75%', '75-80%', '80-85%', '85-90%', '90-95%', '95-100%'
    ]

    perspeedreduction = [
        '0%', '5%', '10%', '15%', '20%',
        '25%', '30%', '35%', '40%', '45%', '50%'
    ]

    int_value = [ 
        0.00, 0.50, 0.55, 0.60, 0.65, 
        0.70, 0.75, 0.80, 0.85, 0.90, 0.95
    ]
    
    int_value2 = [ 
        0.50, 0.55, 0.60, 0.65, 0.70, 
        0.75, 0.80, 0.85, 0.90, 0.95, 1.00
    ]
    
    int_value3 = [ 
        0.00, 0.05, 0.10, 0.15, 0.20, 
        0.25, 0.30, 0.35, 0.40, 0.45, 0.50
    ]    
    list_speed = [(1-i)*speed for i in int_value3]
    list_wave_left = [i * max_wave for i in int_value]
    list_wave_right = [i * max_wave for i in int_value2]
    range_wave = []
    for x,y in zip(int_value, int_value2):
        range_wave.append('{:.3f} - {:.3f}'.format(x*max_wave, y*max_wave))
    

    df = pd.DataFrame(list(zip(range_wave, perwaverange,
                    perspeedreduction, list_speed)),
                    columns =['Wave Range', 'Percentage Wave Range (%)',
                              'Reduce Speed (%)','Ship Speed (knot)'])
    
    df1 = pd.DataFrame(zip(list_wave_left, list_wave_right, list_speed))
    return df, df1

