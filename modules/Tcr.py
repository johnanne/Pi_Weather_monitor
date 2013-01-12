import time , sys , datetime
from time import strftime 

# Time checking routines

class time:
	
	def __init__( self , start_str , end_str ): # should be like ( '09:00:00' , '12:00:00' )
		self.start = datetime.datetime.strptime	( start_str  , '%H:%M:%S') # Lights on
		self.end   = datetime.datetime.strptime	( end_str    , '%H:%M:%S') # Lights off
		self.old_sec = strftime("%S")
		self.old_min = strftime("%M")
		self.old_hrs = strftime("%H")
		if self.start > self.end:
			print ("The start time most be before the end time")
			sys.exit() 

# Rurns true if it`s between the two set times

	def check(self):
		now = strftime("%H:%M:%S")
		T_now =  datetime.datetime.strptime( now , '%H:%M:%S')
		diff1 = (T_now - self.start) ; diff2 = (self.start - T_now)
		diff3 = (T_now - self.end)   ; diff4 = (self.end - T_now)
		return diff1 > diff2 and diff3 < diff4
	
	def new_sec(self):
		sec = strftime("%S") != self.old_sec 
		if sec == True:  self.old_sec = strftime("%S")
		return sec 
		
	def new_min(self):
		min = strftime("%M") != self.old_min 
		if min == True:  self.old_min = strftime("%M")
		return min 	
		
	def new_hrs(self):
		hrs = strftime("%H") != self.old_hrs 
		if hrs == True:  self.old_hrs = strftime("%H")
		return hrs 			