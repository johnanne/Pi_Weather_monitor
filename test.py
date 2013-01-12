#!/usr/bin/env python3

import sys
sys.path.append("/root/mystuff/my_modules") 


# Test Python script to check Xbox controller events
# Requires lego-pi project from https://github.com/zephod/lego-pi
# See http://mattdyson.org/blog/2013/01/using-an-xbox-360-wireless-controller-with-raspberry-pi/
#
# Matt Dyson 05/01/2013
# http://mattdyson.org

import xbox_read

for event in xbox_read.event_stream(deadzone=12000):
	#print  event.key , event.value
	
	if event.key =="LT":
		print ("Left thumb" , event.value )

	if event.key =="RT":
		print ("Right thumb", event.value )
	
	if event.key =="X1":
		print ("pad 1" , event.value )