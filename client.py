#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import base64
import re
import os
import lib
from config import *
from lib import *
from protolib import *
import time
import errno
import setproctitle
import protocol_pb2

reload(sys)
sys.setdefaultencoding('utf8')
setproctitle.setproctitle("py2pclient")
initDB()
class ClientClass:
	def __init__(self):
		self.version = "0.1.1"
		self.iteration = 0
	def whether2Connect2Server(self,server):
		global get
		if server.rejected_connections != 0:
			if clientAfterReachingRejectedConnectionsLimit == "smart_mode":
				if self.iteration % server.rejected_connections == 0:
					return True
				else:
					return False
			if clientAfterReachingRejectedConnectionsLimit == "remove":
				if server in get['hosts']: 
					print "removed ", server
					get['hosts'].discard(server)
				return False
			if clientAfterReachingRejectedConnectionsLimit == "proceed":
				return True
		else:
			return True
	def getFirstRequestData(self,server):
		global get
		data = protocol_pb2.Data()
		data = attachMeta(data)
		data = attachKnownPosts(data)
		return data.SerializeToString()
	def startCycle(self):
		global get
		try: 
			while True:
				for server in get['servers']:
					#print server.host
					if self.whether2Connect2Server(server):
						self.connect(server)
					time.sleep(clientRequestsInterval)
				print "cycle ended"
				break
				time.sleep(clientRequestsInterval)
		except KeyboardInterrupt:
			print " pressed, exiting"
	def connect(self,server):
			global get
			flagToBreak = False
			data2send = self.getFirstRequestData(server)
			iteration = 0 
			while flagToBreak == False:
				if data2send != "":
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					received = ""
#					try:
					sock.connect((server.host, int(server.port))) 
					sock.sendall(str(data2send))
					while True:
						t_received = sock.recv(maxRequestSize)
						if not t_received:
							break
						else:
							received += t_received
#					except BaseException as e:#
#						print "		Error: ", e
#						flagToBreak = True
					iteration+=1
					print "iteration",iteration
					if iteration > 2:#clientMaxIterationCount:
						flagToBreak = True
					data2send = self.processData(server, received)
				else:
					print "Data to send is empty, connection closed"
					sock.close()
					flagToBreak = True
			sock.close()
	def processData(self,server,received_data):
		global get, valid
		rd = protocol_pb2.Data()
		rd.ParseFromString(received_data)
		server, rd = normalizeData(server,rd)
		receivePosts(rd)

		data = protocol_pb2.Data()
		data = attachMeta(data)
		if not hasattr(rd,"requesting"):
			data = attachKnownPosts(data,rd)
		if maxRequestPOW >= server.requestPOW:
			data = requestPosts(server,data,rd)
		data = sendPosts(server,data,rd)
		return data.SerializeToString()
client = ClientClass()
client.startCycle()
