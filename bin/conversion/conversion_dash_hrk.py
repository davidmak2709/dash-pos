#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 09:47:27 2019

@author: toni
"""

import requests
import configparser

response = requests.get('http://api.hnb.hr/tecajn/v1?valuta=USD')
data = response.json()

usd_hrk = float(data[0]['Srednji za devize'].replace(',','.'))
print(usd_hrk)

response = requests.get("https://www.cryptonator.com/api/ticker/dash-usd")
data = response.json()

dash_usd = float(data['ticker']['price'])
print(dash_usd)

dash_hrk = dash_usd * usd_hrk
print("1 DASH = " + str(dash_hrk) + ' kn')

config = configparser.ConfigParser()
config.read('rate.ini')
config['conversion']['rate'] = str(dash_hrk)

with open('rate.ini', 'w') as configfile:
    config.write(configfile)

