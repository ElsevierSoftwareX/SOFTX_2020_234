# Copyright 2020   Dr. Domenico Suriano (domenico.suriano@enea.it)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

### WARNING: GO3_IDSTRING and GO3_BAUD_RATE depend on the settings
### of your 2B Technologies device GO3, therefore check on them and
### update or modify them if necessary.

import _thread
import time
import serial

GO3_IDSTRING = "Ozone,CO2(ppm),Temperature,Pressure,Flow,PDV,Date,Time\r\n"
GO3_BAUD_RATE = 2400
GO3_MEASURES = "o3[ppb];co2[ppm]"
GO3_DEVICE_TYPE = "2B-GO3"
GO3_CONNECTION_TYPE = "usb"
SERIAL_TIMEOUT = 2
MAX_NUM_ATTEMPT = 6
ERR_VAL = "-100"

class Go3:

    def __init__(self):
        self.device_type = GO3_DEVICE_TYPE
        self.identity = ""
        self.connection_type = GO3_CONNECTION_TYPE
        self.baud_rate = GO3_BAUD_RATE
        self.sensors = GO3_MEASURES
        self.strmeas = "0.0;0.0"
        self.port = None
        self.portname = ""
        self.lesteningthread = 0

## the function "connect" check if the device is plugged into serport,
## then returns 1 if the device is found
    def connect(self,serport):
        if (serport.find("ttyACM")>= 0):
            return 0
        if (serport.find("ttyAMA")>= 0):
            return 0
        try:
            self.port = serial.Serial(serport,self.baud_rate, timeout = SERIAL_TIMEOUT, rtscts=0)
        except Exception as e:
            return 0
        num_attempt = 0
        while num_attempt < MAX_NUM_ATTEMPT:
            try:
                self.port.write('h'.encode('utf-8'))
                idstr = self.port.readline().decode()
                if idstr == GO3_IDSTRING:
                    self.lesteningthread = 1
                    ser = serport.split("/")
                    ser1 = ser[-1]
                    self.identity = self.identity + GO3_DEVICE_TYPE + "-" + ser1
                    _thread.start_new_thread(self.__capture,())
                    return 1
                elif idstr == "":
                    num_attempt = num_attempt + 1
                    time.sleep(0.5)
                    continue
                else:
                    num_attempt = num_attempt + 1
                    time.sleep(0.5)
                    continue
            except:
                num_attempt = num_attempt + 1
                time.sleep(0.5)
        return 0

    def getConnectionParams(self):
        return [self.portname,self.baud_rate]

    def getConnectionType(self):
        return self.connection_type

    def getIdentity(self):
        return self.identity

    def getSensors(self):
        return self.sensors

    def getDeviceType(self):
        return self.device_type

## the function "sample" reads the sensor output,
## then returns a string separate by semicolon containing data
## if an error happens, it returns the string with err value: "-100.0"
    def sample(self):
        return self.strmeas
    
    def __capture(self):
        while self.lesteningthread == 1:
            try:
                buf = self.port.readline().decode()
                if len(buf)>2:
                    try:
                        buftemp = buf.split(',')
                        tempfloat = float(buftemp[0])
                        self.strmeas = buftemp[0] + ';' + buftemp[1]
                    except ValueError as ev:
                        self.strmeas = ERR_VAL + ';' + ERR_VAL
            except Exception as e:
                self.strmeas = ERR_VAL + ';' + ERR_VAL


    def terminate(self):
        self.lesteningthread = 0
        try:
            self.port.close()
        except:
            return
    

    def __del__(self):
        self.lesteningthread = 0
        try:
            self.port.close()
        except:
            return
