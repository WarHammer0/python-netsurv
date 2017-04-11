#!/usr/bin/env python
import json
import socket
import binascii
import sys
from codes import check_response_code, lookup_response_code




class IPCam(object):
	def __init__(self, tcp_ip, user="admin", password= "tlJwpbo6", auth = "MD5", tcp_port = 34567):
		self.tcp_ip = tcp_ip	
		self.user = user
		self.password = password
		self.tcp_port = 34567
		self.auth = auth
		self.socket = None

	def connect(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.tcp_ip, self.tcp_port))
		
	def close(self):
		self.socket.close()
	def send_packet(self, msg):	
		self.socket.send(msg)
		data = self.socket.recv(1024)
		return data
	
	def build_packet(self, input_data, message_code, encoding = "ascii"):
		
		if encoding == "hex":
			data = binascii.unhexlify(input_data)

		elif encoding == "ascii":
			data = input_data
		elif encoding == "struct":
			data = json.dumps(input_data)


		high, low = bytes(message_code)
		
		#structure of control flow message packet per spec
		head_flag = "\xFF" 	#One byte fixed value of 0xFF
		version = "\x00" 	#Version number, currently
		reserved_01 = "\x00"	#Reserved, fixed value of 0x00
		reserved_02 = "\x00"	
		session_id = "\x00" 	#Session id, default 0i
		unknown_block_0 = "\x00\x00\x00"
		sequence_number = "\x00"     #Number of packets sent in current session
		unknown_block_1 = "\x00\x00\x00\x00\x00"
		message_byte_1 = chr(low)  	#message code from definition table, little-endian order
		message_byte_2 = chr(high)

		
		data_len = chr(len(data)+1) +"\x00\x00\x00" #Size of data in bytes (padded to 2 bytes)
		data = data + "\x0a"	#ascii data, maximum of 16kb, terminated with a null ascii character
		
		packet = head_flag + version + reserved_01 + reserved_02 + session_id + unknown_block_0 + sequence_number + unknown_block_1 + message_byte_1 + message_byte_2 + data_len + data
		return packet 
	def send(self, input_data, message_code, encoding = "ascii"):
		packet = self.build_packet(input_data, message_code, encoding)
		return self.send_packet(packet)
	def login(self):	
		login_creds_struct = { "EncryptType" : self.auth, "LoginType" : "DVRIP-Web", "PassWord" : self.password, "UserName" : self.user }
		data = self.send(login_creds_struct, 1000, "struct")

		parsed = data[20:].replace(" ", "")

		parsed_json = json.loads(parsed[:-2])
		session_id = parsed_json["SessionID"]
		response_code = parsed_json["Ret"]

		if check_response_code(response_code):
			print "Successfully connected to device at " + host_ip
		else:
			print "Device returned Error " + str(response_code)
			print lookup_response_code(response_code)

	
def bytes(integer):
	return divmod(integer, 0x100)

		
if len(sys.argv) > 1:
	host_ip = str(sys.argv[1])
else:
	host_ip = '192.168.2.108'




cam = IPCam("192.168.2.108")
cam.connect()
cam.login()
cam.close()


