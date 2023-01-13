#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import math
import ship
pd.set_option("display.precision", 3)
import A_C

ST = [0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 
      8, 9, 10, 11, 12, 13, 14, 15, 16, 
      17, 18, 18.5, 19, 19.5, 20
     ]

Simpson = [0.5, 2.0, 1.0, 2.0, 1.5, 
           4.0, 2.0, 4.0, 2.0, 4.0,
           2.0, 4.0, 2.0, 4.0, 2.0,
           4.0, 2.0, 4.0, 2.0, 4.0,
           1.5, 2.0, 1.0, 2.0, 0.5
          ]
def wave_data(wave_height, wave_period):
    #wave_data(lng, lat, time, coordinate, data_set_gelombang)
    g = 32.2
    rho = 3.14
    a = 3.28
    wave_amplitude = (wave_height*a/2)
    wave_length = g*(wave_period**2)/(2*rho)
    wave_velocity = math.sqrt(g*wave_length/(2*rho))
    return wave_amplitude, wave_length, wave_velocity

def breadthperstation(data):
    a = 3.28 #meter to feet#
    #make a new list
    list1 = []
    list2 = [] 
    list3 = []
    for item in data:
        x = (item/40)
        list1.append(x)
        y = x*a
        list2.append(y)
        z = y*2
        list3.append(z)
    dic = {'Station':ST, 'Half Breadth (m)':data, 
           'scale /40': list1, '1/2B (ft)': list2, 
           'B (ft)': list3
          }
    df = pd.DataFrame(dic)
    return df

def CSA(data):
    a = 3.28 ###meter to feet###
    b = 1.9384 ###lb-sec^^2/ft^^4(rho)###
    g = 32.2 
    list1 = []
    list2 = []
    list3 = []
    for item in data:
        x = (item/(40**2))
        list1.append(x)
        y = x*(a**2)
        list2.append(y)
        z= y*b*g
        list3.append(z)
    dic = {'Station':ST, 'Area (m2)':data, 
           'scale /40': list1, 'Area (ft2)': list2, 
           'b (lb/ft)': list3
          }
    df = pd.DataFrame(dic)
    return df

###Arm from LCB###
def Arm_from_LCB(data):
    lst1 = []
    ###reverse list###
    lst2 = []
    x1 = data[12] + data[8]
    x2 = data[12] - data[8]
    lst1.append(x1)
    lst2.append(x2)
    for item in range(13):
        if item >= 1 and item <= 4:
            x1 = x1 - data[13]/2
            x2 = x2 - data[13]/2
            lst1.append(x1)
            lst2.append(x2)
        if item >= 5 and item <= 11:
            x1 = x1 - data[13]
            x2 = x2 - data[13]
            lst1.append(x1)
            lst2.append(x2)
        if item == 12:
            x1 = x1 - data[13]
            x2 = x2 - data[13]
            if x1 >= 0 and x2 <= 0:
                lst1.append(x1)
            elif x1 <= 0 and x2 >= 0:
                lst2.append(x2)
    lst2.reverse()
    lst1.extend(lst2)
    return lst1
        
def az_ayy(nama_excel):
    ###rho fresh water at 59F###
    rho = 1.9384 #lb-sec2/ft4
    phi = 3.14 
    ###input excel###
    xls = pd.ExcelFile(nama_excel)
    ###parsing sheet in excel###
    df2 = pd.read_excel(xls, 'Sheet2',usecols=[1,2])
    ###call ship particular###
    data = ship.new_particular(nama_excel)
    ###Call table for breadth per station###
    bps = breadthperstation(df2['Half Breadth (m)']) #bisa diganti#
    ###Call table for CSA###
    csa = CSA(df2['Luas CSA']) #namanya bisa diganti#
    col1 = ST
    col2 = bps['B (ft)']
    col3 = [data[6] for item in range(len(col1))]
    col4 = csa['Area (ft2)']
    col5 =  Arm_from_LCB(data)
    col6 = [col2[0]*((-0.446)**2)/(2*32.2) for item in range(len(col1))]
    col7 = [x/y for x,y in zip(col2, col3)] #Bn/Tn
    col8 = [x*y for x,y in zip(col2, col3)] #Bn*Tn
    col9 = [x/y for x,y in zip(col4, col8)] #Sn/(Bn*Tn) (Beta-n)
    col9[-1] = 0
    col10 = [A_C.findC(x,y,z) for x,y,z in zip(col9, col6, col7)]
    col11 = [x**2 for x in col2] #Beta-nkuadrat
    col12 = [rho*phi*x/8 for x in col11] #phi*rho*beta-n/8
    col13 = [x*y for x,y in zip(col10, col12)] #an
    simpson = Simpson 
    col15 = [x*y for x,y in zip(col13, simpson)] #product1
    col16 = [x**2 for x in col5] #arm-from-lcb(kuadrat)
    col17 = [x*y for x,y in zip(col13, col16)] #f*h 
    col19 = [x*y for x,y in zip(col17, simpson)] #i*simpson product2
    col20 = [x*y for x,y in zip(col5, col13)] #arm-from-LCB*an
    col22 = [x*y for x,y in zip(col20, simpson)] #product3
    dic = {'No Station': col1, 'Bn': col2, 'Tn':col3, 'Sn':col4,
           'ξ': col5,
           'ξ^2': col16,
           'ωe 2* Bn/2g': col6,
           'Bn/Tn': col7,
           'Bn x Tn': col8,
           'βn': col9,
           'C': col10,
           'an': col13,
           'Product1': col15,
           'Product2': col19,
           'Product3': col22
          }
    df = pd.DataFrame(dic)
    return df

def cC(nama_excel):
    b = 1.9384 ###lb-sec^^2/ft^^4(rho)###
    g = 32.2 
    simpson = Simpson
    data1 = az_ayy(nama_excel)
    col1 = ST
    col2 = data1['Bn']
    col3 = [x*b*g for x in col2]
    col5 = [x*y for x,y in zip(col3, simpson)] #product1
    col6 = data1['ξ^2']
    col7 = [x*y for x,y in zip(col3, col6)]
    col9 = [x*y for x,y in zip(col7, simpson)] #product2
    arm = data1['ξ']
    col10 = [x*y for x,y in zip(col3, arm)]
    col12 = [x*y for x,y in zip(col10, simpson)] #product3
    dic = {'No Station': col1, 'Bn':col2, 'Cn':col3,
           'ξ^2': col6, 
           'Product1': col5,
           'Product2': col9,
           'Product3': col12
          }
    df = pd.DataFrame(dic)
    return df

def bB(nama_excel):
    koef1 = 1.9384 ###lb-sec^^2/ft^^4(rho)###
    koef2 = 32.2 
    nanti_ganti = -0.446
    xls = pd.ExcelFile(nama_excel)
    ###parsing sheet in excel###
    df2 = pd.read_excel(xls, 'Sheet2',usecols=[1,2])
    data1 = az_ayy(nama_excel)
    col1 = ST
    col2 = data1['ωe 2* Bn/2g']
    col3 = data1['Bn/Tn']
    col4 = data1['βn']
    col5 = [A_C.findA(x,y,z) for x,y,z in zip(col4, col2, col3)]
    col6 = [x**2 for x in col5] #apmlitudekuadrat
    col7 = [koef1*(koef2**2)*x/(nanti_ganti**3) for x in col6] #C
    simpson = Simpson
    col9 = [x*y for x,y in zip(col7, simpson)] #product1
    col13 = [x*y*z for x,y,z in zip(col7, data1['ξ^2'], simpson)] #product2
    col16 = [x*y*z for x,y,z in zip(col7, data1['ξ'], simpson)] #product3
    dic = {'No Station': col1, 
           'Ā': col5,
           'Ā**2': col6,
           'C': col7,
           'Product1': col9,
           'Product2': col13,
           'Product3': col16
          }
    df = pd.DataFrame(dic)
    return df

def dehDEH(nama_excel):
    data1 = az_ayy(nama_excel)
    data2 = bB(nama_excel)
    data3 = cC(nama_excel)
    simpson = Simpson
    col1 = ST
    col2 = data1['ξ']
    col3 = data1['an']
    col6 = [x*y*z for x,y,z in zip(col2,col3,simpson)] #product1
    col7 = data2['C']
    col10 = [x*y*z for x,y,z in zip(col2,col7,simpson)] #product2
    col11 = data3['Cn']
    col14 = [x*y*z for x,y,z in zip(col2,col11,simpson)] #product3
    dic = {'No Station': col1, 
           'ξ': col2, 
           'an': col3,
           'bn': col7,
           'cn': col11,
           'Product1': col6,
           'Product2': col10,
           'Product3': col14
          }
    df = pd.DataFrame(dic)
    return df

def m_Lyy(nama_excel):
    koef1 = 1.9384 ###lb-sec^^2/ft^^4(rho)###
    koef2 = 32.2
    xls = pd.ExcelFile(nama_excel)
    ###parsing sheet in excel###
    df2 = pd.read_excel(xls, 'Sheet2',usecols=[1,2,3])
    col1 = ST
    col2 = CSA(df2['Luas CSA'])['b (lb/ft)'] #weightperfoot
    col3 = [ x/koef2 for x in col2] #mn
    simpson = Simpson
    col5 = [x*y for x,y in zip(col3,simpson)] #product1
    col6 = az_ayy(nama_excel)['ξ^2']
    col7 = [x*y for x,y in zip(col3,col6)]
    col9 = [x*y for x,y in zip(col7,simpson)] #product2
    dic = {'No Station': col1, 
           'Weight per foot': col2, 
           'mn': col3,
           'ξ^2': col6,
           'Product1':col5,
           'Product2':col9
          }
    df = pd.DataFrame(dic)
    return df

##calculate value of l in F&M ###
def del_data(data):
    new_data = data.copy()
    indexes = [1, 3, 21, 23]
    for index in sorted(indexes, reverse=True):
        del new_data[index]
    data = new_data.reset_index(drop=True)
    return data
        
def add0start(data):
    new_data = data.copy()
    new_data = del_data(new_data)
    new_data.drop(index=new_data.index[-1],inplace=True)
    use_data = pd.concat([pd.Series([0]), new_data])
    use_data = use_data.reset_index(drop=True)
    return use_data

def add0end(data):
    new_data = data.copy()
    new_data = del_data(new_data)
    new_data.drop(index=new_data.index[0],inplace=True)
    use_data = pd.concat([new_data, pd.Series([0])])
    use_data = use_data.reset_index(drop=True)
    return use_data

def insert_value(data):
    data.insert(1, (data[0] + data[1])/2)
    data.insert(3, (data[2]+ data[3])/2)
    data.insert(21, (data[20]+ data[21])/2)
    data.insert(23, (data[22]+ data[23])/2)
    return data

def new_l(data):
    new_list_l = []
    for index, item in enumerate(data):
        if index == 0:
            new_list_l.append(item)
        if index == (len(data)-1):
            new_list_l.append(item)
        elif index != 0 and index != len(data):
            new_list_l.append(0.5*item)
    new_list = insert_value(new_list_l)
    return new_list_l


def F_M(nama_excel, wave_height, wave_period, vs):
    phi = 3.14
    xls = pd.ExcelFile(nama_excel)
    wave_amplitude = wave_data(wave_height, wave_period)[0] ##harus diubah
    frequency_encounter = -0.446 ###harus diubah
    ###parsing sheet in excel###
    table_az_ayy = az_ayy(nama_excel)
    table_bB = bB(nama_excel)
    table_cC = cC(nama_excel)
    df1 = pd.read_excel(xls, 'Sheet1',usecols=[0,1])
    df2 = pd.read_excel(xls, 'Sheet2',usecols=[1,2,3])
    Sn = table_az_ayy['Sn']
    Bn = table_az_ayy['Bn']
    loa = ship.new_particular(nama_excel)[1]
    col2 = table_az_ayy['ξ']
    col3 = [2*phi*x/loa for x in col2]
    col4 = [math.sin(x) for x in col3]
    col5 = [math.cos(x) for x in col3]
    col6 = [x/y for x,y in zip(Sn, Bn)]
    col7 = [2*x*phi/loa for x in col6]
    col8 = [math.exp(-1*x) for x in col7]
    col9 = table_cC['Cn']
    col10 = [x*wave_amplitude for x in col9]
    col11 = table_az_ayy['an']
    col12 = [x*((-1*wave_amplitude)*(frequency_encounter**2)) for x in col11]
    col13 = [x + y for x,y in zip(col10,col12)]
    sub_data1 = add0start(col11)
    sub_data2 = add0end(col11)
    sub_data3 = add0start(col2)
    sub_data4 = add0end(col2)
    sub_data5 = del_data(col11)
    sub_data6 = del_data(col2)
    cal_l = [(((a-b)/(c-d))+((b-e)/(d-f))) for a,b,c,d,e,f in
            zip(sub_data2,sub_data5,sub_data4,sub_data6,sub_data1,sub_data3)]
    col14 = new_l(cal_l)
    col15 = [vs*wave_amplitude*frequency_encounter*x for x in col14]
    col16 = [x*wave_amplitude*frequency_encounter for x in table_bB['C']]
    col17 = [x-y for x,y in zip(col16,col15)]
    col18 = [x*y for x,y in zip(col13,col4)]
    col19 = [x*y for x,y in zip(col17,col5)]
    col20 = [x+y for x,y in zip(col18,col19)]
    col21 = [x*y for x,y in zip(col13,col5)]
    col22 = [x*y for x,y in zip(col17,col4)]
    col23 = [x-y for x,y in zip(col21,col22)]
    col24 = [x*y for x,y in zip(col20,col8)]
    simpson = Simpson
    Product1 = [x*y for x,y in zip(col24,simpson)]
    col27 = [x*y for x,y in zip(col23,col8)]
    Product2 = [x*y for x,y in zip(col27,simpson)]
    col30 = [x*y for x,y in zip(col24,col2)]
    Product3 = [x*y for x,y in zip(col30,simpson)]
    col33 = [x*y for x,y in zip(col27,col2)]
    Product4 = [x*y for x,y in zip(col33,simpson)]
    dic = {'No Station': ST, 
           'Product1': Product1, 
           'Product2': Product2,
           'Product3': Product3,
           'Product4': Product4
          }
    df = pd.DataFrame(dic)
    return df

def Calculation(nama_excel, wave_height, wave_period, heading_angle, vs):
    g = 32.2
    phi = 3.14
    rho = 1.9384
    data1 = ship.new_particular(nama_excel)
    data2 = az_ayy(nama_excel)
    data3 = bB(nama_excel)
    data4 = cC(nama_excel)
    data5 = m_Lyy(nama_excel)
    data6 = F_M(nama_excel, wave_height, wave_period, vs)
    loa = data1[1]
    beam = data1[4]
    wave_length = wave_data(wave_height, wave_period)[1]
    wave_frequency = math.sqrt(2*phi*g/loa)
    service_speed = vs
    frequency_encounter = wave_frequency - (((wave_frequency**2)*service_speed/g)*math.cos(math.radians(heading_angle)))
    S = data1[13]
    ###added mass###
    az = S*data2['Product1'].sum()/3 #for heaving
    ayy = S*data2['Product2'].sum()/3 #for pitching
    ###damping coefficient###
    b = S*data3['Product1'].sum()/3 #for heaving
    B = S*data3['Product2'].sum()/3 #for pitching
    ###coupling terms###
    d = -1*S*data2['Product3'].sum()/3
    D = d
    e = (-1*S*data3['Product3'].sum()/3) + (service_speed*az)
    E = (-1*S*data3['Product3'].sum()/3) - (service_speed*az)
    h = (-1*S*data4['Product3'].sum()/3) + (service_speed*b)
    H = -1*data4['Product3'].sum()/3
    ###restoring force coefficient###
    c = S*data4['Product1'].sum()/3 #for heaving
    C = (S*data4['Product2'].sum()/3) - (service_speed*E) #for pitching
    ###Mass###
    m = S*data5['Product1'].sum()/3 ##ship mass
    Iyy = S*data5['Product2'].sum()/3 #ship mass moment inertia
    ###Exciting Force and Exciting Moment###
    F1 = S*data6['Product1'].sum()/3 #exciting force 1
    F2 = S*data6['Product2'].sum()/3 #exciting force 2
    F0 = math.sqrt(F1**2 + F2**2) #amplitude of exciting foce
    σ = 180 + math.atan(F2/F1)*180/3.14
    M1 = S*data6['Product3'].sum()/3 #exciting moment 1
    M2 = S*data6['Product4'].sum()/3 #exciting moment 2
    M0 = math.sqrt(M1**2 + M2**2) #amplitude of exciting moment
    τ =  math.atan(M2/M1)*180/3.14
    
    PR = (c - ((az+m)*(frequency_encounter**2)))
    Pi = b*frequency_encounter
    SR = (C - ((Iyy+ayy)*(frequency_encounter**2)))
    Si = B*frequency_encounter
    QR = d*frequency_encounter**2 + h
    Qi = e*frequency_encounter
    RR = D*frequency_encounter**2 + H
    Ri = E*frequency_encounter
    PSR = PR*SR - Pi*Si
    PSi = PR*Si + Pi*SR
    QRR = QR*RR - Qi*Ri
    QRi = Qi*RR + QR*Ri
    PSminQRR = PSR - QRR
    PSminQRi = PSi - QRi
    PSaddQRR = PSR + QRR
    PSaddQRi = PSi + QRi
    PSQRPaddmultiplemin = PSminQRR*PSaddQRR - PSminQRi*PSaddQRi
    
    FR = F1
    Fi = F2
    MR = M1
    Mi = M2
    FSR = FR*SR - Si*Fi
    FSi = FR*Si + SR*Fi
    MQR = MR*QR - Qi*Mi
    MQi = MR*Qi + Mi*QR
    FSminMQR = FSR - MQR
    FSminMQi = FSi - MQi
    QFR = QR*FR - Fi*Qi
    QFi = FR*Qi + Fi*QR
    PSminQFR = PSR - QFR
    PSminQFi = PSi - QFi
    FSminMQmultiplePSminQFR = FSminMQR*PSminQFR - FSminMQi*PSminQFi
    FSminMQmultiplePSminQFi = FSminMQR*PSminQFi + FSminMQi*PSminQFR
    
    MPR = MR*PR - Pi*Mi
    MPi = MR*Pi + PR*Mi
    FRR = FR*RR - Ri*Fi
    FRi = FR*Ri + RR*Fi
    MPminFRR = MPR - FRR
    MPminFRi = MPi - FRi
    MPminFRmultiplePSminQRR = MPminFRR*PSminQRR - PSminQRi*MPminFRi
    MPminFRmultiplePSminQRi = MPminFRR*PSminQRi + PSminQRR*MPminFRi
    
    zR = FSminMQmultiplePSminQFR/PSQRPaddmultiplemin
    zi = FSminMQmultiplePSminQFi/PSQRPaddmultiplemin
    za = math.sqrt(zR**2 + zi**2)
    δz = math.atan(zi/zR)*180/3.14
    θR = MPminFRmultiplePSminQRR/PSQRPaddmultiplemin
    θi = MPminFRmultiplePSminQRi/PSQRPaddmultiplemin
    θ = math.sqrt(θR**2 + θi**2)
    δθ = math.atan(θi/θR)*180/3.14
    
    bndc0 = data1[13]*data3['Product1'].sum()/3
    B33 = (1/(frequency_encounter*data1[11]))*(math.sqrt(g/loa))*bndc0
    bndc1 = data1[13]*data3['Product3'].sum()/3
    B35B53 = (1/(frequency_encounter*data1[11]))*(math.sqrt(g/loa))*bndc1
    bndc2 = data1[13]*data3['Product2'].sum()/3
    B55 = (1/(frequency_encounter*data1[11]))*(math.sqrt(g/loa))*bndc2
    P1 = (frequency_encounter**3)*2*rho*data1[11]*(math.sqrt(g/loa))*B33/((rho*(g**2))*loa)
    P2 = (frequency_encounter**3)*2*rho*data1[11]*(math.sqrt(g/loa))*B35B53/((rho*(g**2))*loa)
    P3 = (frequency_encounter**3)*2*rho*data1[11]*(math.sqrt(g/loa))*4*B55/((rho*(g**2))*loa)
    
    heaving_curve = za
    pitching_curve = θ
    cal_val0 = (loa**2)/(32*(beam**2))
    cal_val1 = P1*(za/heaving_curve)**2
    cal_val2 = P3*(((3.14*loa/wave_length)**2)*(θ*wave_length/(2*3.14*wave_length*pitching_curve)**2))
    cal_val3 = (2*3.14*loa/wave_length)*(wave_length*θ/(2*3.14*pitching_curve))*(za/heaving_curve)*(P2*math.cos(δz-δθ))
    cal_val4 = rho*g*(heaving_curve**2)*((beam**2)/loa)
    cal_val5 = cal_val0*(cal_val1 + cal_val2 - cal_val3)
    model_RAW = cal_val4*cal_val5
    ship_RAW = (model_RAW/0.025)/1000
    if ship_RAW <= 0:
        ship_RAW = ship_RAW*-1
    return ship_RAW
