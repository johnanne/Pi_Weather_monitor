import http.client , sys
import time
import socket
key = "key=your_key"
field_no = "1234567"

def send_data( no_fields , field_data):
	if no_fields < 1 or no_fields > 7:
		print ("The number of fields should be between 1 and 7")
		sys.exit()
	for i in range(no_fields):
		try:
			if type(field_data[i]) != str:  	
				print ( "Field" , i+1 , "is not a string" )
				sys.exit()
		
			dummy = float(field_data[i]) 	 	
				
		except IndexError:
			print ("Field" , i+1 ,  "contents no usable data")
			sys.exit()
		except ValueError:
			print ("I don`t think (", field_data[i] , ") can be converted to a number")
			sys.exit()
	fields = ""
	for i in range( no_fields): 
		fields = fields + "field" + field_no[i] + "=" + field_data[i] + "&"
	params = fields + key
	try:
		conn = http.client.HTTPConnection("api.thingspeak.com:80") 
		headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
		conn.request("POST", "/update", params, headers)
	except 	socket.error:
		sys.exit(55)
	#time.sleep(10)
	#result = conn.getresponse()
	#print("HTTP status code from thinkspeak server: " + str(result.status))
	#return str(result.status)
