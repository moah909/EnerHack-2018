import datetime
import threading
import time
import sys
import Brains_config
import socket
import re
import os
import phue

sys.path.insert(1, '/home/hem/EnerGyanToolKit')
from module.hemSuperClient import HemSuperClient
from phue import Bridge

# Create a new HEM Client
hemSuperClient = HemSuperClient("localhost", 9931)

OPT_LIGHT = Brains_config.OPT_LIGHT
MAX_CHANGE = Brains_config.MAX_CHANGE
OPT_TEMP = Brains_config.OPT_TEMP
FAN_NODE = Brains_config.FAN_NODE
LIGHT_NODE = Brains_config.LIGHT_NODE
UDP_IP = Brains_config.UDP_IP
UPD_PORT = Brains_config.UPD_PORT
b = Bridge(Brains_config.BRIDGE_IP)
CRIT_NODE = Brains_config.CRIT_NODE
NUM_CLUSTERS= Brains_config.NUM_CLUSTERS
POWER_THRESHOLD_inRoom = Brains_config.POWER_THRESHOLD_inRoom
POWER_THRESHOLD_outRoom = Brains_config.POWER_THRESHOLD_outRoom

readLight = 0
currLight = 255
nextLight = 0
temp = 0
inRoom = False
recData = None
clusters = {}
newRequest = False
lastResponse = None

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((UDP_IP, UPD_PORT))

def update(message, address):
    global newRequest
    global lastResponse
    newRequest = True
    lastResponse = message
    print('Rec:', message, address)


def lights():
    global inRoom
    global readLight
    global b
    global temp
    global OPT_LIGHT
    global currLight
    global nextLight
    global critNode
    global clusters
    global LIGHT_NODE

    avLight = 0

    print("inRoom = " + str(inRoom))
    if ((LIGHT_NODE not in CRIT_NODE) and inRoom):
        print ((LIGHT_NODE not in CRIT_NODE) and inRoom)
        b.set_light([1,2], 'on', True)
        print("turning on light")
        time.sleep(.1)
        currLight = b.get_light(1, 'bri')
        for key, value in clusters.iteritems():
            readLight = value['light']
            avLight = avLight + int(readLight)
        avLight = avLight/2
        nextLight = OPT_LIGHT - avLight
        print("currLight = " + str(currLight))
        print("optLight = " + str(OPT_LIGHT))
        print("avLight = " + str(avLight))

        if (abs(nextLight - currLight) < MAX_CHANGE):
            print("nextLight = " + str(nextLight))
        elif (nextLight > currLight):
            nextLight = currLight + MAX_CHANGE
            print("nextLight = " + str(nextLight))
        else:
            nextLight = currLight - MAX_CHANGE
            print("nextLight = " + str(nextLight))

        b.set_light([1,2], 'bri', nextLight)
    else:
        b.set_light([1,2], 'on', False)


def overload():
    global inRoom
    global b
    global CRIT_NODE
    global newRequest
    global lastResponse

    hemSuperClient.sendRequest("/api/getacpoweractive/all")

    while not (newRequest):
        pass

    newRequest = False
    values = lastResponse['VALUE']

    for node in xrange(0,len(values)):

        if (node not in CRIT_NODE):

            if inRoom and (values[node] > POWER_THRESHOLD_inRoom) :
                hemSuperClient.sendRequest("/api/turnoff/" + str(node))

            elif (not inRoom) and (values[node] > POWER_THRESHOLD_outRoom):
                hemSuperClient.sendRequest("/api/turnoff/" + str(node))

def parseData(data):
    recData = dict(re.findall("(\w+):(\d+)", data))
    recData['temp'] = int(recData['temp'])
    recData['light'] = int(recData['light'])
    recData['inRoom'] = (recData['inRoom'] == "1")
    return recData;


def main():
    global critNode
    global clusters
    global NUM_CLUSTERS
    global inRoom

    pid = os.getpid()
    print(pid)
    b.connect()
    b.get_api()

    hemSuperClient.subscribe(update)
    
    while True:

        inRoom = False
        for i in xrange(0,NUM_CLUSTERS * 2 + 1):
            data, addr = sock.recvfrom(1024)
            clusters[addr] = parseData(data)
            inRoom = (inRoom or clusters[addr]['inRoom'])

        lights()
	overload()
        time.sleep(.5)


if __name__ == "__main__":
    main()
