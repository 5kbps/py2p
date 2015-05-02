#!/usr/bin/env python
from config import *
from lib import *
from base64 import b64encode, b64decode
from copy import deepcopy
import time
import sys
import protocol_pb2
reload(sys)  
sys.setdefaultencoding('utf8')

# data
def processData(companion,received_data):
	global get, valid
	updateDB()
	print "____LEN",len(received_data)
	rd = protocol_pb2.Data()
	rd.ParseFromString(received_data)
	companion, rd = normalizeData(companion,rd)
	companion = receivePosts(rd,companion)
	data=protocol_pb2.Data()
	data = attachMeta(data)
#	if len(data.requesting)==0:
	data = attachKnownPosts(data,rd.meta.maxRequestSize)
	if serverMaxRequestPOW >= companion.requestPOW:
		data,companion = requestPosts(companion,data,rd)
	data,companion = sendPosts(companion,data,rd)
	print "LENGTH 		",data.ByteSize()
	companion.toRequest = len(data.requesting)
	companion.toSend = len(data.sending)
	if data.ByteSize()>maxRequestSize:
		print maxRequestSize,"<",data.ByteSize()
		sys.exit(0)
	return data.SerializeToString(),companion

def normalizeData(companion,rd):
	print "		:normalizeData"
	for key in defaultProtocolSettings.keys():
		if hasattr(rd.meta, key):
			setattr(companion,key,getattr(rd.meta,key))
		else:
			if not hasattr(companion,key):
				setattr(companion,key,defaultProtocolSettings[key])
		print "			",key,":",getattr(companion,key)
	return companion, rd
def attachMeta(data):
	print ":attachMeta"
	data.meta.acceptFiles	= acceptFiles
	data.meta.requiredPOW 	= requiredPOW
	data.meta.version 		= py2pVersion
	return data

#posts
def attachKnownPosts(data,limit):
	print ":attachKnownPosts"
	#nd = deepcopy(data)
	for post in get['received']:
		cur_post = data.known.add()
		cur_post.id = post
		cur_post.size = getPostSize(post)
		for tag in get["tags"][post]:
			cur_post.tags.append(tag)
		for language in get["languages"][post]:
			cur_post.languages.append(language)
		if checkLimits(data,maxRequestSize,1024):
			#data = deepcopy(nd)
			print "		[+]",post,": ",cur_post.ByteSize()
		else:
			#nd = deepcopy(data)
			cur_post.remove()
			print "		[-]:",post
			break
	return data
def isGood(known_post):
	return True
def requestPosts(companion,data,rd):
	global get
	print ":requestPosts"
	timeNow = int(time.time())
	nd = deepcopy(data)
	for post in rd.known:
		if not isReceived(post.id) and not isDeleted(post.id) and isGood(post):
			requesting_post = nd.requesting.add()
			requesting_post.id = post.id
			requesting_post.pow, requesting_post.time = getRequestPOW(post,rd.meta.requiredPOW)
			if checkLimits(nd):
				data = deepcopy(nd)
				print "		[+]",post.id
			else:
				nd = deepcopy(data)
				print "		[-]",post.id
				break
		else:
			print "		[--]",post.id
	return data, companion

def sendPosts(companion,data,rd):
	print ":sendPosts"
	nd = deepcopy(data)
	for requesting_post in rd.requesting:
		if checkRequestPOW(requesting_post,companion.requestPOW):
			if isAvaliable(requesting_post.id):
				#post = nd.sending.append(fileContent.decode('unicode_escape') )
				post = nd.sending.append(b64encode(readFile(postsDir+requesting_post.id)))
#				post.ParseFromString(readFile(postsDir+requesting_post.id))
				if checkLimits(nd):
					data = deepcopy(nd)
					print "		[+]:",requesting_post.id,"(",nd.ByteSize(),")"
				else:
					nd = deepcopy(data)
					print "		[-]:",requesting_post.id
					break
				break
			else:
				print "post not avaliable", requesting_post.id
		else:
			print "POW check failed, post was not sent",requesting_post.id
	print "		[data sending length]:",len(data.sending)
	return data, companion
def receivePosts(rd,companion):
	print ":receivePosts"
	for post_source in rd.sending:
		post = protocol_pb2.Post()
		post.ParseFromString(b64decode(post_source))
		if not isDeleted(post.id) and not isReceived(post.id):
			print "		[new post received]:",post.id
			writePost(post)
	return companion
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