#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import base64
import re
import os
import lib
from lib import get, ui, si, valid, parser, datop
import time
import errno
from config import *
import setproctitle
import ssl
import protocol_pb2

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
		global datop
		return_string = ""
		if companion.secretKey == 0:
			companion.secretKey = datop.genKey()
		"""
		if companion.clientKey == 0:
			companion.clientKey = datop.genKey()
			return_string += "cpk:"
		if companion.serverKey == 0:
			companion.serverKey = datop.genKey()
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
		global get,valid,datop
		return_string = ""
		lines = data.split(";")
		for line in lines:
			print line
			return_string += "kkk;"
		return return_string
	def getFirstRequestData(self,companion):
		global datop
		data = protocol_pb2.Data()		
		clientKey = datop.genKey()
		serverKey = datop.genKey()
		secretKey = datop.genKey()
		sendingKey= pow(serverKey,secretKey,clientKey)
		data.keys.clientKey = clientKey
		data.keys.serverKey = serverKey
		data.keys.sendingKey= sendingKey
		data.keys.needKeyRegeneration = True
		companion.clientKey = clientKey
		companion.serverKey = serverKey
		companion.secretKey = secretKey
		data.meta = protocol_pb2.MetaData()
		data.meta.is_public = True
		data.meta.max_posts_at_once = clientMaxPostsCount
		data.meta.max_post_size = clientMaxPostSize
		data.meta.max_request_size = clientRequestLengthLimit
		data.meta.listening_on = serverListeningOn
		return data
	def startCycle(self):
		global get
		for companion in get['hosts']:
			#print companion.host
			if self.whether2Connect2Companion(companion):
				companion = self.connect(companion)
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
	def processData(self,companion,received_data):
		global get, valid
		data = protocol_pb2.Data()
		try:
			data.ParseFromString(received_data)
			if data.p
		except BaseException:
			print "FAILED"
client = Client()
client.startCycle()
