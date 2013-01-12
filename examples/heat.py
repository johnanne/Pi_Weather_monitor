#!/usr/bin/python3

import sys
sys.path.append("/root/mystuff/my_modules") 

import  time , getopt , argparse , pickle , os.path , datetime , sys
from time import strftime
from subprocess import call
from multiprocessing import Process , Value , Array
import I2C , Tcr , SPI , server  # my modules
import thinkspeak as speak
import logging

call("clear")

All_off = 0
Blue = 1
Green = 2
Red = 4
L_Red = 5
Port_a = 0
Port_b = 1
Low_nibble = 0
Hi_nibble = 1

class Main_class:

	def __init__(self):
		self.Cold = 15 # Low than = Blue 
		self.Hot = 20  # Higher than = Red
		self.temp_in = 0
		self.temp_out = 0
		self.Toggle = [ 0 , 0 ]
		self.clear_hi_and_low() 
		self.colour = Blue

	def clear_hi_and_low(self):
		self.Low_temp = 255
		self.Hi_temp = -255
	
	def temp2colour( self , temp ):
		if temp < self.Cold: 								self.colour = Blue
		elif temp >= self.Cold and temp < self.Hot - 2: 	self.colour = Green
		elif temp >= self.Hot -2 and temp < self.Hot: self.colour = L_Red 
		elif temp >= self.Hot:  							self.colour = Red	
	
	def toggle( self , no , max , value1 , value2 ):
		self.Toggle[no] = self.Toggle[no] + 1
		if self.Toggle[no] > max: 
			self.Toggle[no] = 0
			value = value2
		else: value = value1
		return value 
	
if __name__ == '__main__':

	if os.path.isfile("i2c_save.data"):
		mst_obj = pickle.load( open( "i2c_save.data", "rb" ) )
	else:
		mst_obj = Main_class()
	
# Sync High and low temps
	tmp102 = I2C.tmp102(0x48) ;	tmp102.Low_temp = mst_obj.Low_temp ; tmp102.Hi_temp = mst_obj.Hi_temp	

	mst_obj.temp_out = tmp102.read()	

	parser = argparse.ArgumentParser(description="My list of command line args")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-q", "--quiet", action="store_false" , 	help="Stops all screen print outs" )
	group.add_argument("-v", "--verbose", action="store_true" , help="Give a fuller print out" )
	parser.add_argument("-t" , "--thingspeak", action="store_true",  	help="Sends data to the thinkspeak web site" )
	parser.add_argument("--values" , action="store_true" ,	help="Display the local variables" )
	parser.add_argument("--loop" , action="store_true" ,	help="Run in loop" )
	parser.add_argument("--hot" ,  nargs=1 , type=float , help="Sets Hot  " )
	parser.add_argument("--cold" , nargs=1 , type=float , help="Sets Cold " )
	parser.add_argument("--clear"  , action="store_true"  , help="Claer the Hi and Lo values" )
	args = parser.parse_args()

	if args.hot: mst_obj.Hot = args.hot[0]			# Set up Hot and Cold
	if args.cold: mst_obj.Cold = args.cold[0] 

	if args.clear:
		mst_obj.clear_hi_and_low() 
		tmp102.clear_hi_and_low()  
		
	if args.values == True and args.loop == False: 
		print ( 'Low' , mst_obj.Low_temp , 'Hi' , mst_obj.Hi_temp , ' --   Temp in - out' , mst_obj.temp_in  , mst_obj.temp_out ,  ' --   Cold' , mst_obj.Cold , 'Hot' , mst_obj.Hot ) 

	if args.values == False and args.verbose == False and args.loop == True:
		print ("I should really make with a daemon , o.k one day mayme	" )
		
	if args.loop:
		try:
			mtime = Tcr.time( '08:00:00' , '23:59:59' )	
			mcp23017 = I2C.mcp23017(0x23) 
			mcp23017.Set_ddr_all_outs( Port_b )
			mcp3008 = SPI.mcp3008( 0 )
			field_data = [ "" , "" , "" , "" , "" , "" , "" ]
			num_cold = Value('d', mst_obj.Cold )
			num_hot  = Value('d', mst_obj.Hot )
			num_temp = Value('d', mst_obj.temp_out )
			dp = Process( name='loop' , target=server.loop , args=( num_cold , num_hot , num_temp ) ).start()
			logging.basicConfig(filename='/var/log/debug',level=logging.DEBUG)
			while 1:
				mst_obj.temp_out = tmp102.read()
				mst_obj.temp_in = str( round(( round( 1024 - mcp3008.get_adc( 0 , 32 ) , 1 )  - 181.8102 ) / 7.9138 , 1 ) )
				
				if args.verbose:
					print ( '\rLow' , mst_obj.Low_temp , '- Hi' , mst_obj.Hi_temp , ' In ' , mst_obj.temp_in ,' Out ', mst_obj.temp_out ,  ' Cold' , mst_obj.Cold , 'Hot' , mst_obj.Hot , end = "   " )
					sys.stdout.flush() 

				mst_obj.Cold = num_cold.value 
				mst_obj.Hot  = num_hot.value
				num_temp.value = mst_obj.temp_out
	
				while mtime.new_sec() == False:
				
					if mtime.check() == True:	
						mst_obj.temp2colour( mst_obj.temp_out )
						
						if mst_obj.colour == Green:
							mcp23017.Set_gpio_nibble( Port_b , Low_nibble , mst_obj.toggle( 0 , 6 , All_off , mst_obj.colour ) ) 	
						else:
							mcp23017.Set_gpio_nibble( Port_b , Low_nibble , mst_obj.toggle( 0 , 1 , All_off , mst_obj.colour ) ) 						

					else: mcp23017.Set_gpio_nibble( Port_b , Low_nibble , mst_obj.toggle( 0 , 180 , All_off , mst_obj.colour ) ) 	
 						
		
					# time to switch light out		
						
					if mtime.new_min() == True:
						adc = round( 1024 - mcp3008.get_adc( 0 , 32 ) , 1 ) 
						field_data[0] = str( round ( tmp102.read() , 2))
						field_data[1] = str( adc ) 
						field_data[2] = str( round(( adc - 181.8102 ) / 7.9138 , 2 ) )
						p = Process( name='ThingSpeak' , target=speak.send_data , args=( 3 , field_data ))
						p.start()
						#if int(adc) == adc:  
						#	logging.debug(" " + field_data[0] + " " + field_data[1] + " " + field_data[2] ) 
							
					if mtime.new_hrs() == True: 
						pass
						
					time.sleep(.2)
					
				try:
					if  p.is_alive() == True or p.exitcode == 55: mcp23017.Set_gpio_nibble( Port_b , Hi_nibble , Red )
					else: mcp23017.Set_gpio_nibble( Port_b , Hi_nibble , All_off )

				except NameError: pass
			
		except IOError:
			print("I think that was a i2c problem")
			
		except KeyboardInterrupt:
			print (" ")
			mcp23017.Set_gpio_all_off( Port_b )	
			mst_obj.Low_temp = tmp102.Low_temp
			mst_obj.Hi_temp = tmp102.Hi_temp
			pickle.dump( mst_obj , open( "i2c_save.data", "wb" ) )
		
		
# 	SAVING DATA 
	mst_obj.Low_temp = tmp102.Low_temp
	mst_obj.Hi_temp = tmp102.Hi_temp	
	pickle.dump( mst_obj , open( "i2c_save.data", "wb" ) )