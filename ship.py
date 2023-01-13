#!/usr/bin/env python
# coding: utf-8

# In[53]:


import math
import pandas as pd
from math import e
from numpy import arange
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

##import data kapal### 
def particular(nama_excel):
    xls = pd.ExcelFile(nama_excel)
    df = pd.read_excel(xls, 'Sheet1',usecols=[0,1]) 
    df.columns = ['Ship Particular', 'Value']
    Vs = df['Value'][9]
    Lpp = df['Value'][5]
    Loa = 243.84 #belum dibuat tabelnya    
    B = df['Value'][6]
    H = df['Value'][7]
    T = df['Value'][8]
    Lwl = df['Value'][4]
    Cb = 0.651 #belum dibuat tabelnya
    Lcb = 1.702 #belum dibuat tabelnya
    Lcg = -3.4 #belum dibuat tabelnya
    WSA = 1816.636 #belum dibuat tabelnya
    Disp = 4902.545 #belum dibuat tabelnya
    ship_type = df['Value'][1]
    BHP = df['Value'][13]
    engine_speed = df['Value'][15]
    sfoc = df['Value'][14]
    ll = Vs-8 #upperlimit
    ul = Vs+8 #lowelimit
    dic = {'Vs': Vs, 
           'Loa': Loa, 
           'Lwl': Lwl, 
           'Lpp': Lpp,
           'B': B,
           'H': H,
           'T': T,
           'Cb': Cb,
           'Lcb': Lcb,
           'Lcg': Lcg,
           'WSA': WSA,
           'Displacement': Disp,
           'ship type': ship_type,
           'BHP': BHP,
           'engine speed': engine_speed,
           'sfoc': sfoc
          }
    df1 = pd.DataFrame.from_dict(dic, orient='index')
    df1.columns = ['Value']
    return df1, df 

def new_particular(nama_excel):
    data = particular(nama_excel)[0]['Value']
    a = 3.28 #meter to feet#
    b = 1.68 #knot to ft/sec#c
    c = 0.06852 #newton/m to lb/ft
    d = 2.20462 #kg to lb 
    e = 1/40
    Loa = data[1]*a*e #ft
    Lwl = data[2]*a*e #ft
    Vs = data[0]*((Lwl/data[2])**0.5)*b #ft/sec
    Lpp = data[3]*a*e #ft
    B = data[4]*a*e #ft
    H = data[5]*a*e #ft
    T = data[6]*a*e #ft
    Cb = data[7]   
    Lcb = data[8]*a*e #ft
    Lcg = data[9]*a*e #ft
    WSA = data[10]*(a**2)*(e**2) #ft^^2
    Disp = data[11]*d*1000*(e**3) #lb
    ###midship from AP###
    x = Lpp/2
    ###distance between station###
    y = Lpp/20
    return (Vs, Loa, Lwl, Lpp, 
            B, H, T, Cb, Lcb, 
            Lcg, WSA, Disp, x, y
           )   
###function below explains the calculation to find the ship's resistance###
def resistance_calm_water(Vs, nama_excel):
    data = particular(nama_excel)[0]['Value']
    Lpp = data[3]
    B = data[4]
    H = data[5]
    T = data[6]
    Lwl = data[2]
    ship_type = data[12]
    BHP = data[13]
    engine_speed = data[14]
    sfoc = data[15]    
    coef_acc = 'normal section shape'
    rudder_type = ""
    p_sea_water = 1.025        #ton/m3
    knot = 0.514               #m/s
    gravity = 9.81             #m/s**2
    u = 0.0000009425013408     #m2/s
    Vs_in_ms = Vs*knot
    Lwl = 1.04*Lpp
    Fn = Vs_in_ms/math.sqrt(Lwl*gravity)                         #Froude Number
    Cb = 4.22*(-1) + 27.8*math.sqrt(Fn) - 39.1*Fn + 46.6*(Fn**3) #Block Coefficient 
    Cm = 0.977 + 0.085*(Cb - 0.6)                                #midship section coefficient
    Am = Cm*B*T                                                  #area of midship
    Cp = Cb/Cm                                                   #prismatic coefficient
    Cwp = 0.18 + 0.86*Cp                                         #waterplane coefficient
    LCB = -13.5 + 19.4*Cp                                        #Longitudinal Center of Bouyancy
    V = Lwl*B*T*Cb                                               #volume displacement
    A = V*p_sea_water                                            #displacement
    Ta = T
    Tf = T
    #Viscous Resistance
    Rn = Vs_in_ms*Lwl/u #viskositas dinamik
    log_Rn = math.log(Rn,10)
    Cfo = 0.075 / (log_Rn - 2)**2 # friction coefficient
    #Resistance Appendages
    # c is a coefficient accounting for the specific shape of the afterbody 
    if coef_acc == "pram with gondola":
        c_stern = -25
    elif coef_acc == "V-shaped section":
        c_stern = -10
    elif coef_acc == "normal section shape":
        c_stern = 0
    elif coef_acc == "U-shaped sections with Hogner stern":
        c_stern = 10

    c = 1 + 0.011*c_stern 
    #Wetted Surface Area
    Lr_L = 1 - Cp + 0.06*Cp*LCB/(4*Cp-1) #Lr/L(Length of the run)#
    Lwl_V = Lwl**3/V
    #k1 form factor of bare hull 
    k1 = 0.93 + 0.4871*c*((B/Lwl)**1.0681)*((T/Lwl)**0.4611)*((1/Lr_L)**0.1216)*(Lwl_V**0.3549)*(1 - Cp)**-0.6042
    k2 = 1.4
    Abt = 0
    S = Lwl*(2*T + B)*(Cm**0.5)*(0.453+ 0.4425*Cb - 0.2862*Cm - 0.003467*B/T + 0.3696*Cwp) +2.38*Abt/Cb
    ###Wetted Surface of Appendages (Sapp)###
    #size of rudder area according to BKI 
    #c1 for ship type
    if ship_type == "bulk carrier" or ship_type == "tanker":
        c1 = 0.9
    elif ship_type == "tugs" or ship_type == "trawlers":
        c1 = 1.7
    else:
        c1 = 1
    #c2 factor for the rudder type
    if rudder_type == "semi-spader rudders":
        c2 = 0.9
    elif rudder_type == "high lift rudders":
        c2 = 0.7
    else:
        c2 = 1
    
    #c3 factor for rudder profile
    c3 = 1

    #c4 factor for the rudder arrangement
    c4 = 1
    
    Srudder = 2*c1*c2*c3*c4*1.75*Lwl*T/100
    Sbilge_keel = 0
    Sapp = Srudder + Sbilge_keel

    Stotal = S + Sapp #wetted surface area + appendages

    K = k1 + (k2 - k1)*Sapp/Stotal
    
    #Wave making resistance 

    if B/Lwl <= 0.11:
        C4 = 0.2296*(B/Lwl)**(1/3)
    elif 0.11 <= B/Lwl and B/Lwl <= 0.25:
        C4 = B/Lwl
    elif B/Lwl >= 0.25:
        C4 = 0.5 - 0.0625*(Lwl/B)
    
    iE = 125.67*B/Lwl - 162.25*(Cp**2) + 234.32*(Cp**3) + 0.1551*(LCB + 6.8*(Ta -Tf)/T)**3
    d = -0.9
    C1 = 2223105*(C4**3.7861)*((T/B)**1.0796)*(90 - iE)**-1.3757

    if Cp <= 0.8:
        C5 = 8.0798*Cp - 13.8673*(Cp**2) + 6.9844*(Cp**3)
    elif Cp >= 0.8:
        C5 = 1.7301 - 0.7067*Cp

    m1 = 0.01404*(Lwl/T) - 1.7525*(V**(1/3)/Lwl) - 4.7932*(B/Lwl) - C5

    if Lwl/B <= 12:
        lamda = 1.446*Cp - 0.03*(Lwl/B)
    elif Lwl/B > 12:
        lamda = 1.446*Cp - 0.36

    if Lwl**3/V <= 512:
        C6 = -1.69385
    elif 512 <= Lwl**3/V:
        C6 = 1.69385 + (Lwl/V**(1/3)-8)/2.36
    elif Lwl**3/V >= 1727:
        C6 = 0

    m2 = C6*0.4*e**(-0.034*Fn**(-3.29))
    C2 = 1
    C3 = 1 
    radians = math.radians(lamda*Fn**(-2))
    cos = math.cos(radians)
    RW_W = C1*C2*C3*e**(m1*(Fn**d)) + m2*cos
    #Air Resistance
    CA = 0.006*(Lwl + 100)**(-0.16)-0.00205

    #bouyancy
    W = 1.025*V*gravity

    #Air resistance
    Rtotal = 0.5*p_sea_water*1000*(Vs_in_ms**2)*Stotal*(Cfo*K + CA) + RW_W*W #in Newton
    R = Rtotal/1000 #in Kilo Newton
    return R

def power(Vs, Rcw, Raw, nama_excel):
    data = particular(nama_excel)[0]['Value']
    Lpp = data[3]
    B = data[4]
    H = data[5]
    T = data[6]
    Lwl = data[2]
    ship_type = data[12]
    BHP = data[13]
    engine_speed = data[14]
    sfoc = data[15]    
    coef_acc = 'normal section shape'
    rudder_type = ""
    Rtotal = (Rcw + Raw)*1000
    knot = 0.514
    gravity = 9.81             #m/s**2
    u = 0.0000009425013408     #m2/s
    Vs_in_ms = Vs*knot
    Fn = Vs_in_ms/math.sqrt(Lwl*gravity)
    Cb = 4.22*(-1) + 27.8*math.sqrt(Fn) - 39.1*Fn + 46.6*(Fn**3) #Block Coefficient 
    Cm = 0.977 + 0.085*(Cb - 0.6)                                #midship section coefficient
    Am = Cm*B*T                                                  #area of midship
    Cp = Cb/Cm  
    Cwp = 0.18 + 0.86*Cp
    LCB = -13.5 + 19.4*Cp 
    V = Lwl*B*T*Cb
    Rn = Vs_in_ms*Lwl/u #viskositas dinamik
    log_Rn = math.log(Rn,10)
    Cfo = 0.075 / (log_Rn - 2)**2 # friction coefficient

    if coef_acc == "pram with gondola":
        c_stern = -25
    elif coef_acc == "V-shaped section":
        c_stern = -10
    elif coef_acc == "normal section shape":
        c_stern = 0
    elif coef_acc == "U-shaped sections with Hogner stern":
        c_stern = 10

    c = 1 + 0.011*c_stern 
    
    Lr_L = 1 - Cp + 0.06*Cp*LCB/(4*Cp-1) #Lr/L(Length of the run)#
    Lwl_V = Lwl**3/V
    k1 = 0.93 + 0.4871*c*((B/Lwl)**1.0681)*((T/Lwl)**0.4611)*((1/Lr_L)**0.1216)*(Lwl_V**0.3549)*(1 - Cp)**-0.6042
    k2 = 1.4
    Abt = 0
    S = Lwl*(2*T + B)*(Cm**0.5)*(0.453+ 0.4425*Cb - 0.2862*Cm - 0.003467*B/T + 0.3696*Cwp) +2.38*Abt/Cb

    ###Wetted Surface of Appendages (Sapp)###
    #size of rudder area according to BKI 

    #c1 for ship type
    if ship_type == "bulk carrier" or ship_type == "tanker":
        c1 = 0.9
    elif ship_type == "tugs" or ship_type == "trawlers":
        c1 = 1.7
    else:
        c1 = 1
    
    #c2 factor for the rudder type
    if rudder_type == "semi-spader rudders":
        c2 = 0.9
    elif rudder_type == "high lift rudders":
        c2 = 0.7
    else:
        c2 = 1
    
    #c3 factor for rudder profile
    c3 = 1

    #c4 factor for the rudder arrangement
    c4 = 1
    
    Srudder = 2*c1*c2*c3*c4*1.75*Lwl*T/100
    Sbilge_keel = 0
    Sapp = Srudder + Sbilge_keel
    Stotal = S + Sapp #wetted surface area + appendages
    K = k1 + (k2 - k1)*Sapp/Stotal
    #nB = line bearing efficiency
    #nC = Electric tranamission/power conversion efficiency
    #ng = Reduction gear efficiency
    #ng = en electric generator efficiency
    #nH = Hull efficiency + (1-t)/(1-w)
    #nM = electric motor efficiency
    #nO = Propeller open water efficiency
    #nP = propeller behind condition efficiency
    #nR = relative rotative efficiency
    #nS = stern tube bearing efficiency
    #nT = overall transmission efficiency
    
    #Power Engine
    CA = 0.006*(Lwl + 100)**(-0.16) - 0.00205
    EHP = Rtotal*1.15*Vs_in_ms/1000 
    Cv = K*Cfo+CA
    w = 0.3*Cb+10*Cv*Cb-0.1
    t = 0.1
    nH = (1-t)/(1-w)
    THP = EHP/nH
    nO = 0.55       #propeller B-series = 0.5-0.6
    nR = 0.98
    nP = nO*nR
    DHP = THP/nP

    if engine_speed == "medium speed engine":
        nT = 0.975
    elif engine_speed == "low speed engine":
        nT = 0.98
    else:
        nT = 0.975
        
    nBnS = 0.98
    SHP = DHP/nBnS
    BHP = SHP/nT
    return BHP

def displacement(shipspeed, Lwl, B, T):
    gravity = 9.81 #m/s**2
    Vs = shipspeed*0.514
    Fn = Vs/math.sqrt(Lwl*gravity)
    Cb = 4.22*(-1) + 27.8*math.sqrt(Fn) - 39.1*Fn + 46.6*(Fn**3)
    V = Lwl*B*T*Cb
    return V

