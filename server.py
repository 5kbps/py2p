#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import base64
import lib
from lib import get, ui, si, validator, stringify, charoperator, parser
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
"""
class ServerClass:
	# Ctrl-C will cleanly kill all spawned threads
	daemon_threads = True
	# much faster rebinding
	allow_reuse_address = True
	def __init__(self):
		self.version = "0.1.1"
		self.iteration = 0
		self.served = 0
	def computeKeys(self,companion):
		global charoperator
		print "computeFunction"
		return_string = ""
		if companion.serverKey == 0:
			companion.serverKey = charoperator.genKey()
			return_string += "spk:"+str(companion.serverKey)+";"

		if companion.secretKey == 0:
			companion.secretKey = charoperator.genKey()
		if companion.sendingKey == 0 and companion.clientKey != 0 and companion.secretKey != 0 and companion.serverKey != 0 :
			# Generating key to send
			companion.sendingKey = (companion.clientKey**companion.secretKey)%companion.clientKey
			print "SENDING",companion.sendingKey
			return_string += "sk:"+str(companion.sendingKey)+";"
		if companion.sharedKey == 0 and companion.receivedKey != 0 and companion.secretKey != 0 and companion.clientKey != 0:
			#generating sharedKey
			companion.sharedKey = pow(companion.receivedKey,companion.secretKey)%companion.clientKey
			print "COMPUTED SHARED KEY",companion.sharedKey

		print "+++",return_string,"+++"
		return return_string

	def processData(self,companion,data):
		global get, validator
		if data.startswith("aes:"):
			do = "nothing"
		else:
			print "start processing"
			lines = data.split(";")
			return_string = ""
			for line in lines:
				if line.startswith("cpk:"):
					# client sending hid public key
					line = line[4:]
					if validator.key(line):
						companion.hisPublicKey = long(line)
						return_string+= self.computeKeys(companion)
						print "Clients public key received"
					else:
						return_string += "err:301;"
				if line.startswith("spk:"):
					#client sending my public key
					line = line[4:]
					if validator.key(line):
						companion.receivedKey = long(line)
						print "Server public key received"
						self.computeKeys(companion)
					else:
						return_string += "err:302;"
				if line.startswith("ck:"):
					line = line[3:]
					if validator.key(line):
						companion.toSendKey = long(line)
						self.computeKeys(companion)
					else:
						return_string += "err:303;"
			return return_string
	def testProcess(self,data):
		return data + "j"
	def listen(self):
		self.sock = socket.socket()
		self.sock.bind(('',serverPort))
		while True:
			self.sock.listen(serverMaxConnections)
			self.conn,self.addr = self.sock.accept()
			self.iteration = 0
			print "connected", self.addr
			if not self.addr[0] in get['clients']:
				print "new peer", self.addr[0], self.addr[1]
				#print "list",get['clients']
				companion = get['clients'][self.addr[0]] = lib.CompanionClass()
				companion.host = self.addr[0]
				companion.port = self.addr[1]
				#si.save()
			else:
				print "known peer", self.addr[0],self.addr[1]
				companion = get['clients'][self.addr[0]]
			companion = get['clients'][self.addr[0]]
			while True:
				data = ""
				tdata = ""
				data = self.conn.recv(52428800)

				print "RECEIVED: ",data
				if not data:
					break
				self.iteration+=1
				if self.iteration==5:
					print "HEY"
					break

				#self.conn.send(self.processData(companion,data))
				self.conn.send(self.processData(companion, data))
				print "[SENT]"
			#self.conn.close()

myServer = ServerClass()

#except BaseException:
#	server.sock.close()
#	print "ERROR"si.save()

while True:
	sock = socket.socket()
	sock.bind(('', config.serverPort))
	sock.listen(100)
	conn, addr = sock.accept()
	knownPostsSend = False
	print 'connected:',addr

	while True:
		data = ""
		while True:
			try:
				tdata = conn.recv(1024)
			except socket.error, e:
				if isinstance(e.args, tuple):
					print "errno is %d" % e[0]
					if e[0] == errno.EPIPE:
					# remote peer disconnected
						print "Detected remote disconnect"
						conn.close()
				print "socket error: ",e
			if not tdata:
				break
			data += tdata
			if tdata.endswith("[END]"):
				data = data.replace("[END]","")
				break
		#print "[BEGIN]----"
		#print data
		#print "[END]----"
		try:
			conn.send(lib.text(data))
		except socket.error, e:
			if isinstance(e.args, tuple):
				print "errno is %d" % e[0]
				if e[0] == errno.EPIPE:
				# remote peer disconnected
					print "Detected remote disconnect"
					conn.close()
				else:
					# determine and handle different error
					pass
			else:
				print "socket error ", e
			break
	conn.close()
	"""


"""
def pipe_command(arg_list, standard_input=False):
    "arg_list is [command, arg1, ...], standard_input is string"
    
    pipe = subprocess.PIPE if standard_input else None
    subp = subprocess.Popen(arg_list, stdin=pipe, stdout=subprocess.PIPE)
    if not standard_input:
        return subp.communicate()[0]
    return subp.communicate(standard_input)[0]
    """

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
		global charoperator
		print "Generating keys..."
		return_string = ""
		if companion.sharedKey == 0:
			if companion.serverKey == 0:
				companion.serverKey = charoperator.genKey()
				return_string += "spk:"+str(companion.serverKey)+";"
			if companion.clientKey == 0:
				companion.clientKey = charoperator.genKey()
				return_string += "cpk:"+str(companion.clientKey)+";"
			if companion.secretKey == 0:
				companion.secretKey = charoperator.genKey()
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
		global get,validator,charoperator, protocol_pb2
		return_data = protocol_pb2.Data()
		lines = data.split(";")
		for line in lines:	
			print line
	def processData(self,companion,data):
		global get, validator
		print "		Processing data",data
		if data.startswith("?:"):
			return self.processContent(companion, charoperator.DecodeAES(str(data),str(companion.sharedKey)))
		else:
			lines = data.split(";")
			return_string = ""
			for line in lines:
				if line.startswith("cpk:"):
					# client sending hid public key
					line = line[4:]
					if validator.key(line):
						if companion.clientKey == 0:
							companion.clientKey = long(line)
						else: 
							return_string += "err:304;"
						print "Clients public key received"
					else:
						return_string += "err:301;"
				if line.startswith("spk:"):
					#client sending my public key
					line = line[4:]
					if validator.key(line):
						if companion.serverKey == 0:
							companion.serverKey = long(line)
						else:
							return_string += "err:304;"
						print "Server public key received"
					else:
						return_string += "err:302;"
				if line.startswith("sk:"):
					line = line[3:]
					if validator.key(line):
						if companion.receivedKey == 0:
							companion.receivedKey = long(line)
						else:
							return_string += "err:304;"
						print "Received key received",companion.receivedKey
					else:
						return_string += "err:303;"
			if companion.sharedKey != 0:
				
			else:
				return_string+= self.computeKeys(companion)
			return return_string





if __name__ == "__main__":
	global server
	server = serverClass(("127.0.0.1", serverPort), Handler)
	# terminate with Ctrl-C
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		sys.exit(0)