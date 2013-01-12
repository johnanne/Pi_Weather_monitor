from time import sleep 
import sys
import socket , string

# n  = cold , n1 = hot , n2 = temp

			
def loop( n , n1 , n2 ):
	try:
		debug = 0
		commands = [ "read" , "write" ] 
		set_vars = [ "hot" , "cold" ] 
		HOST = ''                 # Symbolic name meaning all available interfaces
		PORT = 50007              # Arbitrary non-privileged port
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		s.listen(1)
		while 1: 
			if debug: print ( "Waiting for connection" ) 
			conn, addr = s.accept()
			if debug: print ( 'Connected by', addr )
			data = conn.recv(1024)
			if data.decode('utf-8') != "Hello":
				conn.send( "Hello error".encode('utf-8') )
				continue
				
			conn.send( "ok".encode('utf-8') )
			data = conn.recv(1024)
			if debug: print ("stage 1 , o.k ")
			
			rec_data =  data.decode('utf-8').split() 
			if rec_data[0].lower() not in commands:
				conn.send( "Command error".encode('utf-8') )
				continue
		
			if rec_data[0].lower() == "write" and rec_data[1] not in  set_vars:
				conn.send( "Command var error".encode('utf-8') )
				continue					
	
			conn.send( "ok".encode('utf-8') )
			data = conn.recv(1024) # waiting for you to ask for it	
			if debug: print ("stage 2 , o.k ")				
			
			if rec_data[0].lower() == "read":
				send_string =  "the temp is " + str(n2.value) + " cold is " + str(n.value) + " hot is " + str(n1.value)
				conn.send( send_string.encode('utf-8') )	
			
			elif rec_data[0].lower() == "write":
				if rec_data[1].lower() == "cold":
					n.value = float( rec_data[2] )
				if rec_data[1].lower() == "hot":
					n1.value = float( rec_data[2] )
				send_string = rec_data[1] + " as now been set to " + rec_data[2]
				conn.send( send_string.encode('utf-8') )
			conn.close()	
			
	except KeyboardInterrupt:
		if 'conn' in dir():
			conn.close()
		sys.exit()

	except socket.error: 
		if 'conn' in dir():   
			conn.close()
		sys.exit()

				