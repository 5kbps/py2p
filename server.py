#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import base64
import lib
from lib import get, ui, si, valid, datop
import time
import errno
from config import *
from socket import error as socket_error
import setproctitle
import ssl
import SocketServer, subprocess, sys 
from threading import Thread 
import protocol_pb2
setproctitle.setproctitle("py2pserver")
class Handler(SocketServer.BaseRequestHandler):
	"One instance per connection.  Override handle(self) to customize action."
	def handle(self):
		global get, si
		# self.request is the client connection
		print "		[Processing a request...]",self.client_address
		data = self.request.recv(1024)  # clip input at 1Kb
		client_addr = self.client_address[0]
		#Getting "companion" object
		if not client_addr in get['clients']:
			print "new peer", client_addr
			#print "list",get['clients']
			companion = get['clients'][client_addr] = lib.CompanionClass()
			companion.host = self.client_address[0]
			companion.port = self.client_address[1]
			companion = get['clients'][client_addr]
			si.save()
		else:
			#print "known peer", self.client_address
			companion = get['clients'][client_addr]
	# 
		reply = server.processData(companion, data)
		if reply is not None and reply is not "":
			print "			Sending a reply",reply
			self.request.send(reply)
		self.request.close()

class serverClass(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	def __init__(self, server_address, RequestHandlerClass):
		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
		self.version = "0.1.1"
		self.iteration = 0
		self.served = 0
		self.port = server_address[1]
		print "[Server started]"
	def computeKeys(self,companion):
		global datop
		print "Generating keys..."
		return_string = ""
		if companion.sharedKey == 0:
			if companion.serverKey == 0:
				companion.serverKey = datop.genKey()
				return_string += "spk:"+str(companion.serverKey)+";"
			if companion.clientKey == 0:
				companion.clientKey = datop.genKey()
				return_string += "cpk:"+str(companion.clientKey)+";"
			if companion.secretKey == 0:
				companion.secretKey = datop.genKey()
				print "secretKey generated"
			if companion.sendingKey == 0 and companion.clientKey != 0 and companion.secretKey != 0 and companion.serverKey != 0 :
				# Generating key to send
				companion.sendingKey = pow(companion.serverKey,companion.secretKey,companion.clientKey)
				print "SENDING",companion.sendingKey
				return_string += "sk:"+str(companion.sendingKey)+";"
			if companion.sharedKey == 0 and companion.receivedKey != 0 and companion.secretKey != 0 and companion.clientKey != 0:
				#generating sharedKey
				companion.sharedKey = pow(companion.receivedKey,companion.secretKey,companion.clientKey)
				print "Computed shared key",companion.sharedKey

		return return_string
	def processContent(self,companion,data):
		global get,valid,datop, protocol_pb2
		return_data = protocol_pb2.Data()
		lines = data.split(";")
		for line in lines:	
			print line
	def processData(self,companion,received_data):
		global get, valid
		data = protocol_pb2.Data()
		data 


if __name__ == "__main__":
	global server
	server = serverClass(("127.0.0.1", serverPort), Handler)
	# terminate with Ctrl-C
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		sys.exit(0)
	except BaseException as e:
		print e 