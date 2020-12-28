import os, glob, time, sys, datetime, pickle
import sqlite3 as lite
import RPi.GPIO as GPIO

## Get session and db name ##
sessionName = pickle.load(open('/home/pi/FermentorApp/sessionName.pkl', 'rb'))
dbName = 'sensorsData.db'

## Setting up probes - three of them on the RPi ##
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
folderList = glob.glob(base_dir + '28*')
deviceFileList = []
for i in folderList:
	p = i + '/w1_slave'
	deviceFileList.append(p)

## Set up GPIO for fan control ##
pin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.setwarnings(False)

## Reads the raw device file info ##
def read_temp_raw(file):
	f = open(file, 'r')
	lines = f.readlines()
	f.close()
	return lines

## Captures temp in deg F and returns list of number values ##
def getTemps():
	tempData = []
	for i in range(len(deviceFileList)):
		lines = read_temp_raw(deviceFileList[i])
		while lines[0].strip()[-3:] != 'YES':
			time.sleep(0.2)
			lines = read_temp_raw()
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos+2:]
			temp_c = float(temp_string) / 1000.0
			temp_f = round(temp_c * 9.0 / 5.0 + 32.0, 1)
			tempData.append(temp_f)
	return tempData

def logData():
    temps = getTemps()
    tempIn, tempOut, tempBeer = temps
    tempSet = pickle.load(open("/home/pi/FermentorApp/tempSet.pkl", "rb"))
    now = datetime.datetime.now()
    date = now.strftime("%c")
    con = lite.connect(dbName)
    cur = con.cursor()
    cur.execute("INSERT INTO " + sessionName + " VALUES((?), (?), (?), (?), (?))", (date, tempIn, tempOut, tempBeer, tempSet))
    con.commit()
    con.close()

    ## Turn fan on our off based on internal temp of fermentor ##
    if float(tempIn) > float(tempSet):
    	GPIO.output(pin, True)
    else:
    	GPIO.output(pin, False)

def displayData():
    c = lite.connect(dbName)
    cur = c.cursor()
    for row in cur.execute("SELECT * FROM " + sessionName):
        print(row)
    c.close()



logData()
