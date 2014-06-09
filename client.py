#!/usr/bin/python
#Version 1.0
#TCP client Version

import yaml
import socket               # Import socket module
import argparse
import sys

#Open Config file
f=open('/opt/ubbshome/config.yml')
config = yaml.safe_load(f)
f.close()

#set my variables
API = config["API"]
PORT = config["SERVER"]["PORT"]
#HOST = config["SERVER"]["HOST"]

BUFFER_SIZE = 1024

#parser = argparse.ArgumentParser(description='Control the server')
#parser.add_argument('char', metavar='N',nargs='+',help='Servername function device')
#parser.add_argument('char', metavar='N', nargs='+',help='an integer for the accumulator')

#args = parser.parse_args
if len(sys.argv) == 1:
	print("-h for help")

elif sys.argv[1] == "-h":
	print("./client HOST list")
	print("./client HOST getstat all")
	print("./client HOST getstat DEVICE")
	print("./client HOST DEVICE off")
	print("./client HOST DEVICE on")
	exit()

if len(sys.argv) == 2:
		print("-h for help")
		exit()


HOST = sys.argv[1]

if len(sys.argv) == 4:
    DATA = sys.argv[2] +" "+ sys.argv[3]
else:
     DATA = sys.argv[2]

#DEVICE = sys.argv[2:]

if "list" in DATA:
	MESSAGE = "list"
elif "getstat" in DATA:
	MESSAGE = "getstat "+ sys.argv[3]
elif "on" in DATA:
	DEVICE = sys.argv[2] + " " + sys.argv[3]
	MESSAGE = DEVICE
elif "off" in DATA:
	DEVICE = sys.argv[2] + " " + sys.argv[3]
	MESSAGE = DEVICE
else:
	MESSAGE = "help"   


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()
print data
