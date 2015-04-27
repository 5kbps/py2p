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
		for post in get['received']:
			cur_post = data.known.add()
			cur_post.id = post.id
			cur_post.size = 100#todo
			for tag in post.tags:
				cur_tag = cur_post.tags.add()	
				cur_tag = tag
			for language in post.languages:
				cur_lang = cur_post.languages.add()
				cur_lang = language
		data.meta.maxPostsAtOnce = clientMaxPostsAtOnce
		data.meta.acceptFiles = clientAcceptFiles
		data.meta.maxPostSize = clientMaxPostSize

"""
		clientKey = datop.genKey()
		serverKey = datop.genKey()
		secretKey = datop.genKey()
		sendingKey= pow(serverKey,secretKey,clientKey)

		data.keys.clientKey = str(clientKey)
		data.keys.serverKey = str(serverKey)
		data.keys.sendingKey= str(sendingKey)
		data.keys.needKeyRegeneration = True
		
#		print "CLIENT KEY",clientKey
		companion.clientKey = clientKey
		companion.serverKey = serverKey
		companion.secretKey = secretKey
"""
		data.meta.max_posts_at_once = clientMaxPostsCount
		data.meta.max_post_size = clientMaxPostSize
		data.meta.max_request_size = clientRequestLengthLimit
		data.meta.listening_on = serverListeningOn
		return data.SerializeToString()
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
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					try:
						sock.connect((companion.host, int(companion.port))) 
						sock.sendall(str(data))
						while True:
							received = sock.recv(1024000)
							#print "rec", received
							if not received:
								break
							else:
								received_data += received
					except BaseException as e:
						print "EXCEPTION", e
					finally:
						sock.close()
					self.iteration+=1
					if self.iteration > clientMaxIterationCount:
						flagToBreak = True
					data = self.processData(companion, received_data)
				else:
					print "Data to send is empty, connection closed"
					sock.close()
					flagToBreak = True
	def processData(self,companion,received_data):
		global get, valid
		data = protocol_pb2.Data()
		try:
			data.ParseFromString(str(received_data))
			return data.SerializeToString()
		except BaseException:
			print "FAILED"
client = Client()
client.startCycle()
