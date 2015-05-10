#!/usr/bin/env python
from config import *
from lib import *
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
	if not raw_msglen or len(raw_msglen)>maxRequestSize:
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
	data = attachKnownPosts(data,0)
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
	print " [received] byte length:",rd.ByteSize()
	rd = normalizeData(rd)
	result['received'] = receivePosts(rd)
	getServers(rd)
	data=protocol_pb2.Data()
	data = attachMeta(data)
	if len(data.requesting)==0:
		data = attachKnownPosts(data,rd)
	data, result['requesting'] = requestPosts(data,rd)
	data,result['sending'] = sendPosts(data,rd)
	result['flagToBreak'] = bool(len(data.requesting) + len(data.sending)) == False
	if data.ByteSize()>maxRequestSize:
		result['flagToBreak'] = True
		sys.excad()
		print data.ByteSize() , "< ",maxRequestSize
		sys.exit(0)
	test = protocol_pb2.Data()
	try:
		test.ParseFromString(data.SerializeToString())
	except BaseException as e:
		print e
		result['flagToBreak'] = True
#	print "->[s] source length",len(data.SerializeToString())
#	print "->[s] byte length",data.ByteSize()
	return data.SerializeToString(),result

def normalizeData(rd):
	print "		:normalizeData"
	return rd
def attachMeta(data):
	global get
	print ":attachMeta"
	data.meta.version 		= py2pVersion
	for c in get['servers'].list:
		#if not c.address.startswith( "127." ) and not c.address.startswith("localhost"):	
		data.meta.servers.append(c.address)
		print "			[+]",c.address
	return data

#posts
def attachKnownPosts(data,rd):
	print ":attachKnownPosts"
	avaliableBytes = maxRequestSize - data.ByteSize()
	for post in get['received']:
		if avaliableBytes > 1024:
			cur_post = data.known.add()
			cur_post.id = post
			avaliableBytes -= cur_post.ByteSize()
#				print "		[+]",post,": ",cur_post.ByteSize()
		else:
			break
	print "		[",len(data.known),"/",len(get['received']),"]"
	return data
def isGood(known_post):
	return True
def requestPosts(data,rd):
	global get
	print ":requestPosts"
	counter = 0
	avaliableBytes = maxRequestSize - data.ByteSize()
	for post in rd.known:
		if avaliableBytes > 1024:
			if not isReceived(post.id) and not isDeleted(post.id) and isGood(post):
				requesting_post = data.requesting.add()
				requesting_post.id = post.id
				avaliableBytes -= requesting_post.ByteSize()
				counter+=1
#				print "		[+]",post.id
			else:
				pass
#				print "		[--]",post.id
		else:
			break
	print "		[",len(data.requesting),"/",len(rd.known),"]"
	return data, counter

def sendPosts(data,rd):
	print ":sendPosts"
	counter = 0
	for requesting_post in rd.requesting:
		avaliableBytes = maxRequestSize - data.ByteSize()
		if isAvaliable(requesting_post.id):
			if avaliableBytes > getFileSize(postsDir+ requesting_post.id,maxPostSize)*3:	
				sbs = data.ByteSize()
				post = data.sending.append( readFile(postsDir+ requesting_post.id))	
				ebs = data.ByteSize()
				rfs = getFileSize(postsDir+ requesting_post.id)
				avaliableBytes -= getFileSize(postsDir+ requesting_post.id)
				print ":	>",sbs,ebs,"(",maxRequestSize,")",rfs,ebs-sbs<rfs*3
				counter += 1
			else:
				print "----",requesting_post.id
#					print "		[+]:",requesting_post.id,"(",nd.ByteSize(),")"
#				break
		else:
			print "post not avaliable", requesting_post.id
	print "		[",len(data.sending),"/",len(rd.requesting),"]"
	return data, counter
def getServers(data):
	global get
	print "		:getServers"
	sl = getServerList()
	if hasattr(data.meta,"servers"):
		for c in data.meta.servers:
			if not c in sl:
#				print "			[+]",c
				s = get['servers'].list.add()
				s.address = c
				s.rejected = 0
				s.received = 0
				s.new = True
			else:
				pass
#				print "			[-]",c," - already in list!"
	saveServers()

def receivePosts(rd):
	counter = 0
	for post_source in rd.sending:
		post = protocol_pb2.Post()#
		post.ParseFromString(post_source)
		if not isDeleted(post.id) and not isReceived(post.id):
#			print "		[new post received]:",post.id
			writePost(post)
			counter += 1
	print ":receivePosts [",counter,"]"
	return counter
#POW
def checkLimits(data,limit=maxRequestSize,increment=0):
	#print "		:checkLimits:",data.ByteSize(),"?",limit+increment
	return data.ByteSize() < limit+increment