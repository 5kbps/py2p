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
checkDirs()
initDB()
class ClientClass:
	def __init__(self):
		self.version = "0.1.1"
		self.iteration = 0
	def whether2Connect2Server(self,server):
		global get
		r = True
		if server.rejected > clientRejectedConnectionsLimit:
			if clientBehaviorAfterReachingRejectedConnectionsLimit == "smart_mode":
				if server.rejected < clientRejectedConnectionsSmartModeLimit:
					if self.iteration % server.rejected == 0:
						print "		[x] +"
						if self.iteration == server.rejected:
							r = self.iteration % 4 == 0
							print " 	[x] 4" 
						r = True
					else:
						print "		[x] -"
						r = False
				else:
					r = False
			if clientBehaviorAfterReachingRejectedConnectionsLimit == "remove":
				r = False
			if clientBehaviorAfterReachingRejectedConnectionsLimit == "proceed":
				r = True
		else:
			r = True
		return r
	def startCycle(self):
		global get
		try: 
			while True:
				for server in get['servers'].list:
					print ":startCycle ",server.address
					#print server.host
					if self.whether2Connect2Server(server):
						try:
							server = self.connect(server)
						except BaseException as e:
							server.rejected += 1
							print "		cannot connect to server:",server.address,"[",server.rejected,"/",clientRejectedConnectionsLimit,"]",e
					print "		[waiting...]"
					time.sleep(clientRequestsInterval)
				print "cycle ended"
				break
				self.iteration += 1
				time.sleep(clientRequestsInterval)
		except KeyboardInterrupt:
			saveServers()
			print " pressed, exiting"
			sys.exit(0)
	def connect(self,server):
			global get
			flagToBreak = False
			data2send = getFirstRequestData()
			iteration = 0 
			while flagToBreak == False:
				if data2send != "":
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					host = server.address.split(":")[0]
					port = toInt(server.address.split(":")[1],5441)
					sock.connect((host, port)) 
					send_msg(sock,data2send)
					received = recv_msg(sock)
					print "iteration",iteration
					try:
						data2send , result = processData(received)
					except BaseException as e:
						print e
						flagToBreak = True
						server.rejected+=1
						break
					if result['flagToBreak'] == True:
						pass
#						flagToBreak = True
					if result['sending'] + result['requesting'] == 0:
						flagToBreak = True
					if iteration >= clientMaxIterationCount:
						print "		clientMaxIterationCount limit reached",server.address
						flagToBreak = True
					iteration+=1
				else:
					print "Data to send is empty, connection closed"
					sock.close()
					flagToBreak = True
			sock.close()
			return server
client = ClientClass()
client.startCycle()
client.startCycle()
client.startCycle()
client.startCycle()
client.startCycle()
client.startCycle()
client.startCycle()
client.startCycle()
client.startCycle()