#!/usr/bin/env python
from config import *
from lib import *
from copy import deepcopy
import time
import sys
import struct
import protocol_pb2
reload(sys)  
sys.setdefaultencoding('utf8')

#networking
def send_msg(sock, msg):
	msg = struct.pack('>I', len(msg)) + msg
	sock.sendall(msg)

def recv_msg(sock):
	raw_msglen = recvall(sock, 4)
	if not raw_msglen:
		return None
	msglen = struct.unpack('>I', raw_msglen)[0]
	# Read the message data
	return recvall(sock, msglen)

def recvall(sock, n):
	data = ''
	while len(data) < n:
		packet = sock.recv(n - len(data))
		if not packet:
			return None
		data += packet
	return data
# data
def getFirstRequestData():
	global get
	data = protocol_pb2.Data()
	data = attachMeta(data)
	data = attachKnownPosts(data)
	return data.SerializeToString()

def processData(received_data):
	global get, valid

	result = {
		"sending":0,
		"requesting":0,
		"flagToBreak":False,
		"received":0
	}
	updateDB()
	rd = protocol_pb2.Data()
	rd.ParseFromString(received_data)
	print " <-[r] byte length:",rd.ByteSize()
	rd = normalizeData(rd)
	result['received'] = receivePosts(rd)
	getServers(rd)
	data=protocol_pb2.Data()
	data = attachMeta(data)
#	if len(data.requesting)==0:
	data = attachKnownPosts(data)
	if serverMaxRequestPOW >= rd.meta.requestPOW:
		data = requestPosts(data,rd)
	data,result['sending'] = sendPosts(data,rd)
	result['flagToBreak'] = bool(len(data.requesting) + len(data.sending)) == False
	if data.ByteSize()>maxRequestSize:
		r['flagToBreak'] = True
	test = protocol_pb2.Data()
	try:
		test.ParseFromString(data.SerializeToString())
	except BaseException as e:
		print e
		result['flagToBreak'] = True
	print "->[s] source length",len(data.SerializeToString())
	print "->[s] byte length",data.ByteSize()
	return data.SerializeToString(),result

def normalizeData(rd):
	print "		:normalizeData"
	if not hasattr(rd.meta,"requestPOW"):
		rd.meta.requestPOW = 0
	return rd
def attachMeta(data):
	global get
	print ":attachMeta"
	data.meta.requestPOW 	= requestPOW
	data.meta.version 		= py2pVersion
	for c in get['servers'].list:
		#if not c.address.startswith( "127." ) and not c.address.startswith("localhost"):	
		data.meta.servers.append(c.address)
		print "			[+]",c.address
	return data

#posts
def attachKnownPosts(data):
	print ":attachKnownPosts"
	for post in get['received']:
		cur_post = data.known.add()
		cur_post.id = post
		cur_post.size = getPostSize(post)
		if post in get['pow']:
			cur_post.pow = get['pow'][post]
		for tag in get["tags"][post]:
			cur_post.tags.append(tag)
		for language in get["languages"][post]:
			cur_post.languages.append(language)
		if checkLimits(data,maxRequestSize,1024):
			print "		[+]",post,": ",cur_post.ByteSize()
		else:
			cur_post.remove()
			print "		[-]:",post
			break
	return data
def isGood(known_post):
	return True
def requestPosts(data,rd):
	global get
	print ":requestPosts"
	
	timeNow = int(time.time())
	nd = deepcopy(data)
	for post in rd.known:
		if not isReceived(post.id) and not isDeleted(post.id) and isGood(post):
			requesting_post = nd.requesting.add()
			requesting_post.id = post.id
			requesting_post.pow, requesting_post.time = getRequestPOW(post,rd.meta.requestPOW)
			if checkLimits(nd):
				data = deepcopy(nd)
				print "		[+]",post.id
			else:
				nd = deepcopy(data)
				print "		[-]",post.id
				break
		else:
			pass
			print "		[--]",post.id
	return data

def sendPosts(data,rd):
	print ":sendPosts"
	nd = deepcopy(data)
	counter = 0
	for requesting_post in rd.requesting:
		if checkRequestPOW(requesting_post,rd.meta.requestPOW):
			if isAvaliable(requesting_post.id):
				post = nd.sending.append( readFile(postsDir+ requesting_post.id) )				
				if checkLimits(nd):
					data = deepcopy(nd)
					counter += 1
					print "		[+]:",requesting_post.id,"(",nd.ByteSize(),")"
				else:
					nd = deepcopy(data)
					print "		[-]:",requesting_post.id
					break
			else:
				print "post not avaliable", requesting_post.id
		else:
			print "POW check failed, post was not sent",requesting_post.id
	print "		[data sending length]:",len(data.sending)
	return data, counter
def getServers(data):
	global get
	print "		:getServers"
	sl = getServerList()
	if hasattr(data.meta,"servers"):
		for c in data.meta.servers:
			if not c in sl:
				print "			[+]",c.address
				s = get['servers'].list.add()
				s.address = c
				s.rejected = 0
				s.received = 0
				s.new = True
			else:
				pass
				print "			[-]",c," - already in list!"
	saveServers()

def receivePosts(rd):
	print ":receivePosts"
	counter = 0
	for post_source in rd.sending:
		post = protocol_pb2.Post()#
		post.ParseFromString(post_source)
		if not isDeleted(post.id) and not isReceived(post.id):
			print "		[new post received]:",post.id
			writePost(post)
			counter += 1
	return counter
#POW
def checkRequestPOW(requesting_post,requiredPOW):
	if requiredPOW != 0:
		if abs(time.time() - requesting_post.time )< clientMaxPOWTimeShift:
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
def getRequestPOW(post,requiredPOW):
	if requiredPOW != 0:
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
	else:
		powValue = 0;
		timeNow = 0;
	return powValue, timeNow
def checkLimits(data,limit=maxRequestSize,increment=0):
	#print "		:checkLimits:",data.ByteSize(),"?",limit+increment
	return data.ByteSize() < limit+increment