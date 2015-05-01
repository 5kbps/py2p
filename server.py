#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, os, time, setproctitle, SocketServer, subprocess, sys, protocol_pb2
from lib import *
from config import *
from threading import Thread

setproctitle.setproctitle("py2pserver")

initDB()

class Handler(SocketServer.BaseRequestHandler):
	def handle(self):
		global get
		# self.request is the client connection
		print "		[Processing a request...]",self.client_address
		received_data = self.request.recv(52428800)  # clip input at
		#Getting "client" object
		print "GOT IT", len(received_data)
		client_address = self.client_address
		if not self.client_address[0] in get['clients']:
			print "new peer", client_address[0]
			#print "list",get['clients']
			client = get['clients'][client_address[0]] = Client()
			client.host = self.client_address[0]
			client.port = self.client_address[1]
		else:
			print "known peer", self.client_address
			client = get['clients'][client_address[0]]
		reply = server.processData(client, received_data)
		if reply is not None and reply is not "":
			print "			Sending a reply", len(reply)
			self.request.send(reply)
		self.request.close()

#class serverClass(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
class serverClass(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	def __init__(self, server_address, RequestHandlerClass):
		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
		self.served = 0
		self.port = server_address[1]
		print "[Server started]"

	def attachMeta(self,data):
		data.meta.maxPostsAtOnce = serverMaxPostsAtOnce
		data.meta.acceptFiles = serverAcceptFiles
		data.meta.maxPostSize = serverMaxPostSize
		data.meta.maxPostSize = serverMaxPostSize
		return data
	def attachKnown(self,data,received_data):
		global get
		clientPostList = set()
		for knownPost in received_data.known:
			clientPostList.add(knownPost.id)
		for post in get['received']:
			if not post in clientPostList:
				cur_post = data.known.add()
				cur_post.id = post
				cur_post.size = getPostSize(post)
				for tag in get["tags"][post]:
					cur_post.tags.append(tag)
				for language in get["languages"]:
					cur_post.languages.append(language)
		return data
	def processData(self,client,received_data):
		global get, valid
		rd = protocol_pb2.Data()
		rd.ParseFromString(received_data)
		rd = self.normalizeData(client,rd)
		#^ received data
		data=protocol_pb2.Data()
		data = self.attachMeta(data)
		data = self.attachKnown(data,rd)
		# ^data to send
		return data.SerializeToString()
	def normalizeData(self,client,rd):
		if not hasattr(rd.meta, "maxPostsAtOnce"):
			rd.meta.maxPostsAtOnce = clientMaxPostsAtOnce
		if not hasattr(rd.meta, "clientMaxPostSize"):
			rd.meta.maxPostSize = clientMaxPostSize
		if not hasattr(rd.meta, "clientRequestLengthLimit"):
			rd.meta.maxRequestSize = clientRequestLengthLimit
		if not hasattr(rd.meta, "acceptFiles"):
			rd.meta.acceptFiles = clientAcceptFiles
		return rd

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