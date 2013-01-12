from quick2wire.spi import *

#		
#   mcp3008 = SPI.mcp3008( 0 )	
#   a = mcp3008.get_adc( 0 , 32 )
#

class mcp3008:

	def __init__( self , cs ):
		self.cs = cs
		self.device = SPIDevice( 0, cs )
		
	def get_adc( self , channel , Samples ):
		M_samples = 0
		for loop in range(1 , Samples + 1 ): 
			reply  = self.device.transaction( duplex_bytes( 1 , ( ( 8 + channel ) << 4 ) , 0 )  )[0]
			adc_value =  (( reply[1] & 3 ) << 8 ) + reply[2]
			M_samples = M_samples + adc_value
		return M_samples / Samples

