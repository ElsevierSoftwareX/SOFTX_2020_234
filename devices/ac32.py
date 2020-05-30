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

### WARNING: AC32_ADDRESS, AC32_PORT, AC32_ID_STRING and AC32_UNITS
### depend on the settings of your Environnement device AC32,
### therefore check on them and update or modify them if necessary.

import socket
import time

AC32_ADDRESS = "192.168.20.43"
AC32_PORT = 8000
AC32_ID_STRING = "AC32"
AC32_UNITS = "no[ppb];nox[ppb];no2[ppb]"
AC32_DEVICE_TYPE = "ENVIRONNEMENT-AC32"
AC32_CONNECTION_TYPE = "eth"
SOCKET_TIMEOUT = 2
MAX_NUM_ATTEMPT = 4
ACK = '\x06'
ERR_VAL = "-100"

class Ac32:

    def __init__(self):
        self.device_type = AC32_DEVICE_TYPE
        self.connection_type = AC32_CONNECTION_TYPE
        self.address = AC32_ADDRESS
        self.port = AC32_PORT
        self.portname = str(AC32_PORT)
        self.identity = ""
        self.sensors = AC32_UNITS
        self.sk = None
        self.status = 'U'
        self.alarm = None
    
## the function "connect" check if the device is plugged into Ethernet port,
## then returns 1 if the device is found        
    def connect(self):
        try: 
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sk.settimeout(SOCKET_TIMEOUT)
        except Exception as e:
            return 0        
        command = chr(2) + AC32_ID_STRING + "16"
        tocalc = command.encode()
        c1,c2 = self.BCCcalc(tocalc)
        command = command + chr(c1) + chr(c2) + chr(3)
        tent = 0
        while tent < MAX_NUM_ATTEMPT:
            try:
                sent = self.sk.sendto(command.encode(), (self.address,self.port))
                data1, server = self.sk.recvfrom(1024)
                data = data1.decode()
            except socket.timeout:
                if tent >= MAX_NUM_ATTEMPT:
                    return 2
                else:
                    tent = tent + 1
                    time.sleep(0.2)
                    continue
            except Exception as e:
                if tent >= MAX_NUM_ATTEMPT:
                    return 3
                else:
                    tent = tent + 1
                    time.sleep(0.2)
                    continue                    
            if (data[0]!= ACK) and (tent>=MAX_NUM_ATTEMPT):
                return 4
            if (data[0]!= ACK) and (tent<MAX_NUM_ATTEMPT):
                tent = tent + 1
                time.sleep(0.2)
                continue 
            if (data[0]== ACK):
                self.identity = self.identity + str(data[1:5])
                self.status = data[13]
                self.alarm = str(data[14]) + str(data[15])
                return 1

    def getConnectionParams(self):
        return [self.address,self.portname]

    def getConnectionType(self):
        return self.connection_type

    def getIdentity(self):
        return self.identity

    def getSensors(self):
        return self.sensors

    def getDeviceType(self):
        return self.device_type

    def BCCcalc(self,mb):
        BCC = 0
        for i in range(1,len(mb)):
            BCC = BCC ^ mb[i]
        BCC1 = BCC>>4|48
        if BCC1 > 57:
            BCC1+=7
        BCC2 = (BCC&15)|48
        if BCC2 > 57:
            BCC2+=7
        return(BCC1,BCC2)

## the function "sample" reads the sensor output,
## then returns a string separate by semicolon containing data
## if an error happens, it returns the string with err value: "-100.0"
    def sample(self):
        command = chr(2) + AC32_ID_STRING + "16"
        tocalc = command.encode()
        c1,c2 = self.BCCcalc(tocalc)
        command = command + chr(c1) + chr(c2) + chr(3)
        tent = 0
        while tent < MAX_NUM_ATTEMPT:
            try:
                sent = self.sk.sendto(command.encode(), (self.address,self.port))
                data1, server = self.sk.recvfrom(1024)
                data = data1.decode()
            except socket.timeout:
                tent = tent + 1
                time.sleep(0.2)
                continue
            except Exception as e:
                tent = tent + 1
                time.sleep(0.2)
                continue
            if data[0]!= ACK:
                tent = tent + 1
                time.sleep(0.2)
                continue
            else:
                self.status = data[13]
                self.alarm = str(data[14]) + str(data[15])
                str2 = data[17:]
                strm = str2.split(' ')
                try:
                    val1 = float(strm[0])
                    val2 = float(strm[0])
                    val3 = float(strm[0])
                except:
                    return ERR_VAL + ";" + ERR_VAL + ";" + ERR_VAL
                if val1 < 0:
                    val1str = "0.0"
                else:
                    val1str = strm[0]
                if val2 < 0:
                    val2str = "0.0"
                else:
                    val2str = strm[1]
                if val3 < 0:
                    val3str = "0.0"
                else:
                    val3str = strm[2]
                return val1str + ';' + val2str + ';' + val3str
        return ERR_VAL + ";" + ERR_VAL + ";" + ERR_VAL


    def terminate(self):
        try:
            self.sk.close()
        except:
            return


    def __del__(self):
        try:
            self.sk.close()
        except:
            return

