#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, os, time, setproctitle, SocketServer, subprocess, sys, protocol_pb2
from lib import *
from config import *
from threading import Thread
from protolib import *
import struct
setproctitle.setproctitle("py2pserver")

initDB()
def send_msg(sock, msg):
	# Prefix each message with a 4-byte length (network byte order)
	msg = struct.pack('>I', len(msg)) + msg
	sock.sendall(msg)

def recv_msg(sock):
	# Read message length and unpack it into an integer
	raw_msglen = recvall(sock, 4)
	if not raw_msglen:
		return None
	msglen = struct.unpack('>I', raw_msglen)[0]
	# Read the message data
	return recvall(sock, msglen)

def recvall(sock, n):
	# Helper function to recv n bytes or return None if EOF is hit
	data = ''
	while len(data) < n:
		packet = sock.recv(n - len(data))
		if not packet:
			return None
		data += packet
	return data

class Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		global get
		# self.request is the client connection
		print "		[Processing a request...]",self.client_address
		received_data = ""
		'''
		while True:
			t_data = self.request.recv(maxRequestSize)
			print " 	!REQUEST [",len(t_data),"/",len(received_data),"]"
			if len(t_data)==0: 
				break
			if  len(t_data)+len(received_data)>=maxRequestSize:
				break
			received_data += t_data
		'''
#		received_data = self.request.recv(maxRequestSize)		#Getting "client" object
		received_data = recv_msg(self.request)
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
			send_msg(self.request,reply)
#			self.request.send(reply)
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