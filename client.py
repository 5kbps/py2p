#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import base64
import re
import os
import lib
from lib import get, ui, si, validator, stringify, charoperator, parser
import time
import errno
from config import *
import setproctitle
import ssl


setproctitle.setproctitle("py2pclient")

class Client:
	def __init__(self):
		self.version = "0.1.1"
		self.iteration = 0
	def whether2Connect2Companion(self,companion):
		global get
		if companion.rejected_connections != 0:
			if clientAfterReachingRejectedConnectionsLimit == "smart_mode":
				if self.iteration % companion.rejected_connections == 0:
					return True
				else:
					return False
			if clientAfterReachingRejectedConnectionsLimit == "remove":
				if companion in get['hosts']: 
					print "removed ", companion
					get['hosts'].discard(companion)
				return False
			if clientAfterReachingRejectedConnectionsLimit == "proceed":
				return True
		else:
			return True
	def computeKeys(self,companion):
		global charoperator
		return_string = ""
		if companion.secretKey == 0:
			companion.secretKey = charoperator.genKey()
		"""
		if companion.clientKey == 0:
			companion.clientKey = charoperator.genKey()
			return_string += "cpk:"
		if companion.serverKey == 0:
			companion.serverKey = charoperator.genKey()
			return_string += "spk:"
		"""
		if companion.sendingKey ==0 and companion.clientKey != 0 and companion.serverKey != 0 and companion.secretKey != 0:
			companion.sendingKey= pow(companion.serverKey,companion.secretKey,companion.clientKey)
			#print "Computed sending key ",companion.sendingKey
		if companion.sharedKey ==0 and companion.receivedKey != 0 and companion.secretKey != 0 and companion.clientKey != 0:
			companion.sharedKey = pow(companion.receivedKey,companion.secretKey,companion.clientKey)
			#print "Computed shared key: ",companion.sharedKey
			#return_string += ""
		return return_string
	def processContent(self,companion,data):
		global get,validator,charoperator
		return_string = ""
		lines = data.split(";")
		for line in lines:
			print line
			return_string += "kkk;"
		return return_string
	def processData(self,companion,data):
		global get, validator		
		return_string = ""
		if data.startswith("?:"):
			# Encrypted data
			reply = self.processContent(charoperator.base64Decode(charoperator.DecodeAES(data,str(companion.sharedKey))))
			return charoperator.base64Encode(charoperator.EncodeAES(reply,str(companion.sharedKey)))
		else:
			lines = data.split(";")
			for line in lines:
				if line.startswith("spk:"):
					#server sending my public key
					line = line[4:]
					if validator.key(line):
						if companion.serverKey == 0:
							companion.serverKey = parser.parseKey(line)
						else:
							return_string += "err:304:keys already sent;"
					else:
						return_string += "err:302:key not valid;"
				if line.startswith("sck:"):
					line = line[4:]
					if validator.key(line):
						if companion.clientKey == 0:	
							companion.clientKey = long(line)
						else:
							return_string += "err:304:keys already sent"
					else:
						return_string += "err:304;"
				if line.startswith("sk:"):
					# server sending his computed key
					line = line[3:]
					if validator.key(line):
						if companion.receivedKey == 0:
							companion.receivedKey = long(line)
						else:
							return_string +="err:304:keys already sent;"
					else:
						return_string += "err:303;"
			return_string+= self.computeKeys(companion)
		return return_string
	def getFirstRequestData(self,companion):
		global charoperator
		return_string = ""
		print "Generating keys..."
		if companion.sharedKey == 0:
			companion.clientKey = int(os.urandom(clientPublicKeyLength).encode('hex'),16)
			companion.serverKey = int(os.urandom(clientPublicKeyLength).encode('hex'),16)
			companion.secretKey = int(os.urandom(clientPublicKeyLength).encode('hex'),16)
			self.computeKeys(companion)
			return_string += "cpk:"+str(companion.clientKey)+";"
			return_string += "spk:"+str(companion.serverKey)+";"
			return_string += "sk:"+str(companion.sendingKey)+";[E]"
			#print "Keys generated: ",return_string
		else:
			return_string += "?:"+str(charoperator.base64Encode(charoperator.EncodeAES("hello",str(companion.sharedKey))))+";"
		return return_string
	def startCycle(self):
		global get
		for companion in get['hosts']:
			#print companion.host
			if self.whether2Connect2Companion(companion):
				companion = self.connect(companion)
	def testProcess(self,data):
		return data + "i"
	def connect(self,companion):
			global get
			flagToBreak = False
			data = self.getFirstRequestData(companion)
			self.iteration = 0 
			while flagToBreak == False:
				if data != "":
					# Create a socket (SOCK_STREAM means a TCP socket)
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					try:
					    # Connect to server and send data
						sock.connect((companion.host, int(companion.port)))
						sock.sendall(data)
					    # Receive data from the server and shut down
						received = sock.recv(1024)
					finally:
						sock.close()

					#print "Sent:     {}".format(data)
					#print "Received: {}".format(received)
					self.iteration+=1 
					if self.iteration > clientMaxIterationCount:
						flagToBreak = True
					data = self.processData(companion, received)
					print companion.sharedKey
				else:
					print "Data to send is empty, connection closed"
					sock.close()
					flagToBreak = True
"""
		self.sock = socket.socket()
		self.sock.settimeout(clientRequestTimeout)
#		try:
		self.sock.connect((companion.host,int(companion.port))) 

		while True:
			print "[Connected...]"
			self.sock.send(self.getFirstRequestData(companion))
			print "[Data sent]" 
			data = ""
			tdata = ""
			self.iteration = 0
			while True:
				data = ""
				tdata = ""
				self.iteration += 1
				try:
					data = self.sock.recv(1024)
					print "request sent, data received"
					print "requested"
				except socket.error,e:
					print "Socket error ",e
				if not data:
					break
				print "i got ",data
				#self.sock.send(self.processData(companion,data))
				self.sock.send(self.processData(companion,data))
			print "Cycle was broken"
			"""
			#	except socket.error, e:
			#		ui.log("Cannot send data "+companion.host+":"+str(companion.port)+" : " +str(e))

	#		except socket.error, e:
	#			ui.log("Cannot connect to "+companion.host+":"+str(companion.port))
	#			sock.close()

client = Client()
client.startCycle()
