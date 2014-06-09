#!/usr/bin/python
#Version 1.0
#TCP server version
#

import yaml
import socket               # Import socket module
import RPi.GPIO as GPIO
import time
from apscheduler.scheduler import Scheduler
import logging

#Open Config file
f=open('config.yml')
config = yaml.safe_load(f)
#config=yaml.load(f)
f.close()

#set my variables with info from the config file
API = config["API"]
PORT = config["SERVER"]["PORT"]
HOST = config["SERVER"]["HOST"]
BUFFER_SIZE = config["SERVER"]["BUFFER_SIZE"]
API = config["API"]
APPNAME = config["PROGNAME"]
LOGFILE = config["LOGFILE"]
LOGFORMAT = config["LOGFORMAT"]
LOG_LEVEL = config["LOG_LEVEL"]
OUTPUTS = config["OUTPUT"].keys()
INPUTS = config["INPUT"].keys()
PAIRS = config["PAIR"].keys()

#Logging
logger = logging.getLogger(APPNAME)
hdlr = logging.FileHandler(LOGFILE)
#formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
formatter = logging.Formatter(LOGFORMAT)
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(LOG_LEVEL)

#logger.error('We have a problem')
#logger.info('While this is just chatty')

#Prints the OUTPUTS
#print config['OUTPUT'].keys()
#Prints the INPUTS
#print config['INPUT'].keys()
#prints GPIO of device
#print config["OUTPUT"]["TV"]["GPIO"]

#Setup my GPIO Stuff
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def channeltooutput():
	for p in PAIRS:
		inp=config["PAIR"][p]["IN"]
		out=config["PAIR"][p]["OUT"]	
		print("in "+str(inp)+ " out " +str(out))

channeltooutput()

#Setup Outputs
for o in OUTPUTS:
	pin = config["OUTPUT"][o]["GPIO"]
	GPIO.setup(pin, GPIO.OUT)
	#Set them to all off
	GPIO.output(pin,GPIO.HIGH)	

#Setup Inputs
for i in INPUTS:
	pin = config["INPUT"][i]["GPIO"]
	GPIO.setup(pin, GPIO.IN) 

	
#Create functions for buttons
#Need To Fix
for p in PAIRS:
	out = config["PAIR"][p]["OUT"]
	def p(channel):
		if(GPIO.input(out) == 1):
			print("Turning "+p+" on")
               		logger.info('Turning '+p+ ' on')
                	GPIO.output(out, GPIO.LOW)
		else:
			print("Turning "+p+" off")
                	logger.info('Turning '+p+ ' off')
                	GPIO.output(out,GPIO.HIGH)
#Button Stuff

def Pair1(channel):
        #print("Button 1 pressed!")
        #print("Note how the bouncetime affects the button press")
        if(GPIO.input(14) == 1):
                output1 = "ON"
                print("Turning "+output1+" output1")
                GPIO.output(14, GPIO.LOW)
        else:
                output1 = "OFF"
                print("Turning "+output1+" output1")
                GPIO.output(14,GPIO.HIGH)


def Pair2(channel):
        #print("Button 2 pressed!")
        #print("Note how the bouncetime affects the button press")
        if(GPIO.input(15) == 1):
                output2 = "ON"
                print("Turning "+output2+" output2")
                GPIO.output(15, GPIO.LOW)
        else:
                output2 = "OFF"
                print("Turning "+output2+" output2")
                GPIO.output(15,GPIO.HIGH)



def Pair(channel):
	print("channel" + str(channel))
	if(GPIO.input(14) == 1):
                print("Turning ON "+str(channel))
                GPIO.output(14, GPIO.LOW)
        else:
                print("Turning OFF "+str(channel))
                GPIO.output(14,GPIO.HIGH)
	
#GPIO.add_event_detect(2, GPIO.RISING, callback=Pair1, bouncetime=300)
#GPIO.add_event_detect(3, GPIO.RISING, callback=Pair2, bouncetime=300)

for p in PAIRS:
	print (p)
	pin = config["PAIR"][p]["IN"]
	GPIO.add_event_detect(pin, GPIO.RISING, callback=Pair, bouncetime=300)


#Scheduling stuff
sched = Scheduler()
sched.start()

def sunrise_function():
    print "Turn off at Sunrise"
    logger.info('Turn off at Sunrise')
    GPIO.output(23,GPIO.HIGH)

def sunset_function():
    print "Turn on At Sunset"
    logger.info('Turn on at Sunset')
    GPIO.output(23,GPIO.LOW)

#Turns off output at 6:00
sched.add_cron_job(sunrise_function, day_of_week='*', hour=6, minute=00)
#Turns on output at 17:30
sched.add_cron_job(sunset_function, day_of_week='*', hour=17, minute=30)


#Start server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)
print("Waiting for Connections")
logger.info('Waiting for Connections')
while True:
	c, addr = s.accept()
	print 'Connection address:', addr
	ip = str(addr[0])
	print(ip)
	logger.info('Connection From: ' +ip)
	while True:
		data = c.recv(BUFFER_SIZE)
		datac = data.rstrip()
		#print(device)
		#print(device[1])
		if datac == "list":
			devices = str(OUTPUTS)
        	        c.send(devices+ "\n")
		elif "all" in datac:
			for o in OUTPUTS:
        			pin = config["OUTPUT"][o]["GPIO"]	
				if(GPIO.input(pin) == 0):
					c.send(o+" is On\n")	
				else:
					c.send(o+" is Off\n")
		elif "getstat" in datac:
			device = datac.split()
			pin = config["OUTPUT"][device[1]]["GPIO"]
			if(GPIO.input(pin) == 0):
				c.send("On\n")
			else:
				c.send("Off\n")

		elif "on" in datac:
			device = datac.split()
			pin = config["OUTPUT"][device[0]]["GPIO"]
			if(GPIO.input(pin) == 0):
				c.send(device[0]+ " Is Already On\n")
			else:
				c.send("Turned " +device[0]+ " on\n")
				GPIO.output(pin, GPIO.LOW)
				
		elif "off" in datac:
			device = datac.split()
                        pin = config["OUTPUT"][device[0]]["GPIO"]
			if(GPIO.input(pin) == 1):
				c.send(device[0]+ " is Off\n")
			else:
				c.send("Turned " +device[0]+ " on\n")
				GPIO.output(pin, GPIO.HIGH)
			
		elif "help" in datac:
			c.send("./client HOST list \n ./client HOST getstat all \n ./client HOST getstat DEVICE \n ./client HOST DEVICE off \n ./client HOST DEVICE on \n")
		
		elif "quit" in datac:
			break
		
		else:
			c.send("help\n")
			#c.close()		
		if not data: break
		print "received data:", data
		logger.info('Received data: ' +data)
		#c.send(data)  # echo
c.close()
