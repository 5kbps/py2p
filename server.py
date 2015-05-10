#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, os, time, setproctitle, SocketServer, subprocess, sys, protocol_pb2
from lib import *
from config import *
from threading import Thread
from protolib import *
import struct
setproctitle.setproctitle("py2pserver")
checkDirs()
initDB()
class Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		global get
		# self.request is the client connection
		print "		:hadle ",self.client_address
		received_data = recv_msg(self.request)
		client_address = self.client_address
		address = client_address[0]
		
		if not address in get['shared_keys']:
			reply = genKeys2(received_data, address)
			print ">>>",len(reply)
		else:
			reply, result = processData(received_data)
		if reply is not None and reply is not "":
			print "			Sending a reply", len(reply)
			send_msg(self.request,reply)
		self.request.close()

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
	server = serverClass(("", serverPort), Handler)
	# terminate with Ctrl-C
	server.allow_reuse_address = True
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print " pressed, exiting"
		server.shutdown()
		sys.exit(0)