#!/usr/bin/env python3

# Reading from the tmp102 , with below zero temperatures working

from quick2wire.i2c import *   

CHIP_BASE_ADDRESS = 0x48

with I2CMaster(1) as master:
	Hi_byte , Low_byte = master.transaction( reading(CHIP_BASE_ADDRESS , 2))[0]
	if Hi_byte & 0x80 == 0x80:	
		Hi_byte = (Hi_byte + 1 & 0xff) 
		heat = 0 - (( Hi_byte << 4) | ( Low_byte >> 4)) * 0.0625  
	else:
		heat = (( Hi_byte << 4) | ( Low_byte >> 4)) * 0.0625  
	print ( heat )