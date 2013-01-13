from quick2wire.i2c import *   
import sys

def error_check( value , lower_limit , higher_limit , msg ):
	if value > higher_limit or value < lower_limit:
		print ( msg )
		sys.exit()	
	# easy to change and raise a error instead
	
class tmp102:

# Below zero problem fixed , I hope !!

	def __init__( self , CHIP_BASE_ADDRESS ):
		self.CHIP_BASE_ADDRESS = CHIP_BASE_ADDRESS
		self.Low_temp = 255
		self.Hi_temp = -255
		
	def __str__(self):
		return str(self.read())

# ( High byte * 256 ) + Low byte , then / 16 and the result * 0.0625
 
	def read(self):	
		with I2CMaster(1) as master:
			Hi_byte , Low_byte = master.transaction( reading(self.CHIP_BASE_ADDRESS , 2))[0]
			if Hi_byte & 0x80 == 0x80:	
				Hi_byte = (Hi_byte + 1 & 0xff) 
				heat = 0 - (( Hi_byte << 4) | ( Low_byte >> 4)) * 0.0625  
			else:
				heat = (( Hi_byte << 4) | ( Low_byte >> 4)) * 0.0625  
			if heat > self.Hi_temp: 	self.Hi_temp = heat
			if heat < self.Low_temp:	self.Low_temp = heat
			return heat

	def clear_hi_and_low(self):
		self.Low_temp = 255
		self.Hi_temp = -255


class mcp32016:    #not tested , but should work   

# REGISTER ADDRESSES
# GP0 =     0x0
# GP1 =     0x1
# OLAT0 =   0x2
# OLAT1 =   0x3 
# IPOL0 =   0x4 
# IPOL1 =   0x5 
# IODIR0 =  0x6 
# IODIR1 =  0x7 
# INTCAP0 = 0x8 
# INTCAP1 = 0x9 
# IOCON0 =  0xA 
# IOCON1 =  0xB 

	def __init__(self , CHIP_BASE_ADDRESS ):
		self.CHIP_BASE_ADDRESS = CHIP_BASE_ADDRESS

	def Set_ddr_all_outs( self , port):
		self.Set_ddr( port , 0 )

	def Set_gpio( self , port , data ):
		error_check( port , 0 , 1 ,   "ERROR Set_gpio ( port must be 0 or 1 , byte ) ")
		error_check( data , 0 , 255 , "ERROR Set_gpio ( not a byte value )")
		with I2CMaster(1) as master:	
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port , data ))

	def Set_ddr(self , port , data ):
		error_check( port , 0 , 1 ,   "ERROR Set_ddr ( port must be 0 or 1 , byte ) ")
		error_check( data , 0 , 255 , "ERROR Set_ddr( not a byte value )")
		if port == 0 :   port = 0x6
		elif port == 1 : port = 0x7
		with I2CMaster(1) as master:	
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port , data ))		

	def Set_gpio_all_on( self , port ):
		self.Set_gpio( port , 0xff )

	def Set_gpio_all_off( self , port ):
		self.Set_gpio( port , 0 )	

class mcp23017:

# REGISTER ADDRESSES
	IODIRA 		= 0x0	#	I/O DIRECTION REGISTER
	IODIRB		= 0x1	
	IPOLA 		= 0x2	#	INPUT POLARITY REGISTER
	IPOLB 		= 0x3 
	GPINTENA 	= 0x4	#	INTERRUPT-ON-CHANGE CONTROL REGISTER
	GPINTENB 	= 0x5
	DEFVALA 	= 0x6	#	DEFAULT VALUE REGISTER
	DEFVALB 	= 0x7
	INTCONA 	= 0x8	#	INTERRUPT CONTROL REGISTER
	INTCONB 	= 0x9
	IOCON 		= 0xa	#	I/O EXPANDER CONFIGURATION REGISTER
	IOCON 		= 0xb
	GPPUA 		= 0xc	#	GPIO PULL-UP RESISTOR REGISTER
	GPPUB 		= 0xd
	INTFA 		= 0xe	#	INTERRUPT FLAG REGISTER
	INTFB 		= 0xf
	INTCAPA 	= 0x10	#	INTERRUPT CAPTURE REGISTER
	INTCAPB 	= 0x11
	GPIOA 		= 0x12	#	GENERAL PURPOSE I/O PORT REGISTER
	GPIOB 		= 0x13		
	OLATA 		= 0x14	#	OUTPUT LATCH REGISTER
	OLATB 		= 0x15

	def __init__(self , CHIP_BASE_ADDRESS ):
		self.CHIP_BASE_ADDRESS = CHIP_BASE_ADDRESS

	def Set_ddr_all_outs( self , port):
		self.Set_ddr( port , 0 )

	def Set_ddr( self , port , data ):
		error_check( port , 0 , 1 ,   "ERROR Set_ddr ( port must be 0 or 1 ) ")
		error_check( data , 0 , 255 , "ERROR Set_ddr ( not a byte value )")	
		with I2CMaster(1) as master:	
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port , data ))

	def Set_gpio(self , port , data ):
		error_check( port , 0 , 1 ,   "ERROR Set_gpio ( port must be 0 or 1 ) ")
		error_check( data , 0 , 255 , "ERROR Set_gpio ( not a byte value )")	
		if port == 0 :   port = mcp23017.GPIOA 
		elif port == 1 : port = mcp23017.GPIOB
		with I2CMaster(1) as master:	
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port , data ))		

	def Set_gpio_all_on( self , port ):
		self.Set_gpio( port , 0xff )

	def Set_gpio_all_off( self , port ):
		self.Set_gpio( port , 0 )	
		
	def Set_gpio_nibble(self , port , nib , data ):
		error_check( port , 0 , 1 ,   "ERROR Set_gpio_nibble ( port must be 0 or 1 ) ")
		error_check( nib , 0 , 1 ,    "ERROR Set_gpio_nibble( NIB must be 0 or 1  ) ")		
		error_check( data , 0 , 15 ,  "ERROR Set_gpio( not a nibble value )" )			
		if port == 0 :   port = mcp23017.GPIOA
		elif port == 1 : port = mcp23017.GPIOB
		if nib == 0: mask = 0xf0
		if nib == 1: data = data << 4 ; mask = 0xf 
		with I2CMaster(1) as master:
			old_data = master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port ) , reading(self.CHIP_BASE_ADDRESS, 1 ))[0][0]
			data = ( old_data & mask ) + data 
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port , data ))				
	
	def gpio_read( self , port ):
		error_check( port , 0 , 1 ,   "ERROR gpio_read ( port must be 0 or 1 ) ")	
		if port == 0 :   port = mcp23017.GPIOA
		elif port == 1 : port = mcp23017.GPIOB
		with I2CMaster(1) as master:
			data = master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port ) , reading(self.CHIP_BASE_ADDRESS, 1 ))[0][0]
			return data
			
	def gpio_read_nibble( self , port , nib ):
		error_check( port , 0 , 1 ,   "ERROR gpio_read_nibble ( port must be 0 or 1 ) ")		
		error_check( nib , 0 , 1 ,   "ERROR gpio_read_nibble ( NIB must be 0 or 1 ) ")
		if port == 0 :   port = mcp23017.GPIOA
		elif port == 1 : port = mcp23017.GPIOB
		with I2CMaster(1) as master:
			data = master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port ) , reading(self.CHIP_BASE_ADDRESS, 1 ))[0][0]
			if nib == 0: data = data & 0xf
			if nib == 1: data = (( data & 0xf0 ) >> 4)				
			return data	

	def Set_all_pull_ups( self , port ):
		error_check( port , 0 , 1 ,   "ERROR Set_pull_ups ( port must be 0 or 1 ) ")	
		if port == 0 :   port = mcp23017.GPPUA
		elif port == 1 : port = mcp23017.GPPUB
		with I2CMaster(1) as master:
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port , 0xff ))		

	def Clear_all_pull_ups( self , port ):
		error_check( port , 0 , 1 ,   "ERROR Claer_pull_ups ( port must be 0 or 1 ) ")	
		if port == 0 :   port = mcp23017.GPPUA
		elif port == 1 : port = mcp23017.GPPUB
		with I2CMaster(1) as master:
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , port , 0 ))	
			
	def Set_gpio_bit( self , port , bit ):
		error_check( port , 0 , 1 , "EEROR Set_gpio_bit( port muast be 0 or 1 )")

class mcp23008:	

# REGISTER ADDRESSES
	IODIR 	= 0x0	#	I/O DIRECTION REGISTER 
	IPOL	= 0x1	#	INPUT POLARITY PORT REGISTER
	GPINTEN	= 0x2	#	INTERRUPT-ON-CHANGE PINS
	DEFVAL	= 0x3	#	DEFAULT VALUE REGISTER
	INTCON	= 0x4	#	INTERRUPT-ON-CHANGE CONTROL REGISTER
	IOCON	= 0x5	#	I/O EXPANDER CONFIGURATION REGISTER
	GPPU	= 0x6	#	GPIO PULL-UP RESISTOR REGISTER
	INTF	= 0x7	#	INTERRUPT FLAG REGISTER
	INTCAP	= 0x8	#	INTERRUPT CAPTURED VALUE FOR PORT REGISTER (Read-only)
	GPIO	= 0x9	#	GENERAL PURPOSE I/O PORT REGISTER 
	OLAT	= 0xA	#	OUTPUT LATCH REGISTER 0
	
	def __init__(self , CHIP_BASE_ADDRESS ):
		self.CHIP_BASE_ADDRESS = CHIP_BASE_ADDRESS

	def Set_ddr_all_outs( self ):
		self.Set_ddr( 0 )
		
	def Set_ddr_all_ins( self ):
		self.Set_ddr( 0xff )
		
	def Set_ddr( self , data ):
		error_check( data , 0 , 255 , "ERROR Set_ddr ( not a byte value )")		
		with I2CMaster(1) as master:	
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.IODIR , data ))
		
	def Set_gpio_all_on( self ):
		self.Set_gpio( 0xff )

	def Set_gpio_all_off( self ):
		self.Set_gpio( 0 )			

	def Set_gpio( self , data ):
		error_check( data , 0 , 255 , "ERROR Set_gpio ( not a byte value )")		
		with I2CMaster(1) as master:	
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPIO , data ))		
			
	def Set_gpio_nibble( self , nib , data ):
		error_check( nib , 0 , 1 ,    "ERROR Set_gpio_nibble( NIB must be 0 or 1  ) ")		
		error_check( data , 0 , 15 ,  "ERROR Set_gpio( not a nibble value )" )			
		if nib == 0: mask = 0xf0
		if nib == 1: data = data << 4 ; mask = 0xf 
		with I2CMaster(1) as master:
			old_data = master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPIO ) , reading(self.CHIP_BASE_ADDRESS, 1 ))[0][0]
			data = ( old_data & mask ) + data 
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPIO , data ))				
			
	def gpio_read_nibble( self , nib ):
		error_check( nib , 0 , 1 ,   "ERROR gpio_read_nibble ( NIB must be 0 or 1 ) ")
		with I2CMaster(1) as master:
			data = master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPIO ) , reading(self.CHIP_BASE_ADDRESS, 1 ))[0][0]
			if nib == 0: data = data & 0xf
			if nib == 1: data = (( data & 0xf0 ) >> 4)				
			return data	
			
	def gpio_read( self ):
		with I2CMaster(1) as master:
			data = master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPIO ) , reading(self.CHIP_BASE_ADDRESS, 1 ))[0][0]
			return data
			
	def Set_pull_ups( self , data ):
		with I2CMaster(1) as master:
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPPU , data ))	
			
	def Set_all_pull_ups( self ):
		with I2CMaster(1) as master:
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPPU , 0xff ))		

	def Clear_all_pull_ups( self ):
		with I2CMaster(1) as master:
			master.transaction( writing_bytes( self.CHIP_BASE_ADDRESS , mcp23008.GPPU , 0 ))			
		