# Thermometer Program v.0.1

# This program reads temperatures from RPi Model B+ and stores them to SQL database.

# Copyright  (C) 2014 Mika Kaikkonen
# Email mika78_kaikkonen@hotmail.com
# Web: http://kaikkonen.atspace.eu

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Imports
import mysql.connector
import os
import glob
import time

config = {
    'user': 'sqluser',
    'password': 'sqlpwd',
    'host': 'localhost',
    'database': 'demo',
    'raise_on_warnings': True,
}

#initialize the device 
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

device_folder2 = glob.glob(base_dir + '28*')[1]
device_file2 = device_folder2 + '/w1_slave'

device_folder3 = glob.glob(base_dir + '28*')[2]
device_file3 = device_folder3 + '/w1_slave'

device_folder4 = glob.glob(base_dir + '28*')[3]
device_file4 = device_folder4 + '/w1_slave'

def read_temp_raw(file):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(file):
    lines = read_temp_raw(file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return ( "%.2f" % temp_c )

counter = 0
connection = mysql.connector.connect(**config)
print(connection)
cursor = connection.cursor()
add_temp = ("INSERT INTO Measurements "
    "(Sensor1, Sensor2, Sensor3, Sensor4, Note) "
    "VALUES (%s, %s, %s, %s, %s)")
while True:
    # Get temperatures and print them
    try:
        device1 = str(read_temp(device_file))
        print("Sensor 1: " + device1)
        device2 = str(read_temp(device_file2))
        print("Sensor 2: " + device2)
        device3 = str(read_temp(device_file3))
        print("Sensor 3: " + device3)   
        device4 = str(read_temp(device_file4))
        print("Sensor 4: " + device4)
        # For every 60 secs, store the temparatures to the MySQL database
        if counter == 5:
            try:
                # Store to MySQL
                print("Store to MySQL")
                data_temp = (device1, device2, device3, device4, "Auto")
                cursor.execute(add_temp, data_temp)
            except (KeyboardInterrupt, SystemExit):
                print("Rollback1")
                connection.rollback()
                raise
            except:
                print("Rollback2")  
                connection.rollback()
                raise
            else:
                print("Commit")
                connection.commit()

        time.sleep(1)
        counter += 1
        print(counter)
    except:
        print("Connection close")
        cursor.close()
        connection.close()
        raise
