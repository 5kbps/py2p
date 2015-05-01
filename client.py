#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import base64
import re
import os
import lib
from lib import *
import time
import errno
from config import *
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
	def attachMeta(self,data):
		data.meta.maxPostsAtOnce = clientMaxPostsAtOnce
		data.meta.acceptFiles    = clientAcceptFiles
		data.meta.maxPostSize    = clientMaxPostSize
		data.meta.version 		 = 1
		return data
	def attachKnownPosts(self,data):
		global get
#		print get['received']
		for post in get['received']:
			print "		>",post
			cur_post = data.known.add()
			cur_post.id = post
			cur_post.size = getPostSize(post)
			for tag in get["tags"][post]:
				cur_post.tags.append(tag)
			for language in get["languages"]:
				cur_post.languages.append(language)
		return data
	def getFirstRequestData(self,server):
		global get
		data = protocol_pb2.Data()
		data = self.attachMeta(data)
		data = self.attachKnownPosts(data)
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
					try:
						sock.connect((server.host, int(server.port))) 
						sock.sendall(str(data2send))
						while True:
							t_received = sock.recv(clientRequestSize)
							if not t_received:
								break
							else:
								received += t_received
						print "GOT IT", len(received)
					except BaseException as e:
						print "		Error: ", e
						flagToBreak = True
					iteration+=1
					if iteration > 1:#clientMaxIterationCount:
						flagToBreak = True
					data2send = self.processData(server, received)
				else:
					print "Data to send is empty, connection closed"
					sock.close()
					flagToBreak = True
			sock.close()
	def requestPosts(self,server,data,rd):
		for post in rd.known:
			if not isReceived(post.id) and not isDeleted(post.id) and checkLimits(server,rd):
				req = data.requesting.add()
				req.id = post
				if server.requestPOW != 0:
					req.pow , req.time= self.getRequestPOW(post.id,server.requestPOW)
					print "POW ",server.requestPOW,"to request ",post.id," calculated"
		return data
	def attachPost(self,data,postid):
		if isReceived(postid):
			if not isDeleted(postid) and not isLocal(postid):

	def sendPosts(self,server,data,rd):
		for requesting_post in rd.requesting:
			if checkRequestPOW(server,requesting_post):
				data = attachPost(data,requesting_post.id)
	def checkRequestPOW(self,requesting_post):
		if clientRequiredPOW != 0:
			if abs(time.time() - requesting_post.time )< clientMaxPOWTimeShift
				t_pow_1 = hex2bin(md5(requesting_post.id+str(requesting_post.time)+str(requesting_post.pow)))
				t_pow_2 = hex2bin(md5(str(requesting_post.pow)+requesting_post.id+str(requesting_post.time)))
				if t_pow_1[:clientRequiredPOW] == t_pow_2[:clientRequiredPOW]:
					return True
				else:
					return False
			else:
				return False
		else:
			return True
	def getRequestPOW(self,post.id,requiredPOW):
		powValue = 1
		timeNow = int(time.time())
		strTimeNow = str(timeNow)
		while True:
			strPowValue = str(powValue)
			t_pow_1 = hex2bin(md5(post.id+strTimeNow+strPowValue))
			t_pow_2 = hex2bin(md5(strPowValue+post.id+strTimeNow))
			if t_pow_1[:requiredPOW] == t_pow_2[:requiredPOW]:
				break
			else:
				powValue += 1
		return powValue, timeNow
	def processData(self,server,received_data):
		global get, valid
		rd = protocol_pb2.Data()
		rd.ParseFromString(received_data)
		server, rd = self.normalizeData(server,rd)

		data = protocol_pb2.Data()
		data = self.attachMeta(data)
		data = self.attachKnownPosts(data)
		if clientMaxRequestPOW >= server.requestPOW:
			data = self.requestPosts(server,data,rd)
		data = self.sendPosts(server,data,rd)
		return rd.SerializeToString()
	def checkLimits(self,server,rd):
		# Проверка, не исчерпаны ли ограничения на общий размер запроса и количество постов
		_re = False
		if server.requestingPostsCount < rd.meta.maxPostsAtOnce:
			if server.requestSize < rd.meta.maxRequestSize:
				_re = True
		return _re 
	def normalizeData(self,server,rd):
		for key in defaultProtocolSettings.keys():
			if hasattr(rd.meta, key):
				setattr(server,key,getattr(rd.meta,key))
			else:
				if not hasattr(server,key):
					setattr(server,key,defaultProtocolSettings[key])
		server.requestingPostsCount = 0
		server.requestSize  = 0
		return server, rd

client = ClientClass()
client.startCycle()
