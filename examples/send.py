#!/usr/bin/env python3

import quick2wire.i2c as quick
from quick2wire.i2c import *   

import sys
import socket
import time

HOST = "127.0.0.1"
PORT = 50007

def send(  my_str , p_out = True ):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(1)
	s.connect((HOST, PORT))
	try:
		# send "Hello"
		s.send( "Hello".encode('utf-8') )
		# receice , and check for "ok" or exit 
		data = s.recv(1024)
		if data.decode('utf-8') != "ok":
			print ( data.decode('utf-8') )
			s.close()
			sys.exit()
		
		# send command set and check for "ok" or exit
		s.send( my_str.encode('utf-8') )
		data = s.recv(1024)
		if data.decode('utf-8') != "ok":
			print ( data.decode('utf-8') )
			s.close()
			sys.exit()
		
		# send anything to trigger incoming data
		s.send( " ".encode('utf-8') )
		data = s.recv(1024)
	
		if p_out: print (data.decode('utf-8'))

	except socket.timeout as exc :
		print ("The other side is waiting for") 

cold = input("Cold temp value ? ")
hot = input("Hot temp value  ? ")
		
if cold: send ( "write cold " + str(cold) , False ) 
if hot: send ( "write hot " + str(hot) , False ) 
send ( "read" )

