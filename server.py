#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, os, time, setproctitle, SocketServer, subprocess, sys, protocol_pb2
from lib import *
from config import *
from threading import Thread
from protolib import *
setproctitle.setproctitle("py2pserver")

initDB()

class Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		global get
		# self.request is the client connection
		print "		[Processing a request...]",self.client_address
		received_data = self.request.recv(maxRequestSize)
		#Getting "client" object
		print "GOT IT", len(received_data)
		client_address = self.client_address
		if not self.client_address[0] in get['companions']:
			print "new peer", client_address[0]
			#print "list",get['clients']
			client = Client()
			client.host = self.client_address[0]
			client.port = self.client_address[1]
		else:
			print "known peer", self.client_address
			client = get['companions'][client_address[0]]
		reply,client = processData(client, received_data)
		get['companions'][client_address[0]] = client
		if reply is not None and reply is not "":
			print "			Sending a reply", len(reply)
			self.request.send(reply)
		self.request.close()

#class serverClass(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
class serverClass(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	def __init__(self, server_address, RequestHandlerClass):
		SocketServer.TCPServer.allow_reuse_address = True
		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
		SocketServer.TCPServer.allow_reuse_address = True
		self.served = 0
		self.port = server_address[1]
		print "[Server started]"
if __name__ == "__main__":
	global server
	server = serverClass(("127.0.0.1", serverPort), Handler)
	# terminate with Ctrl-C
	server.allow_reuse_address = True
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print " pressed, exiting"
		server.shutdown()
		sys.exit(0)