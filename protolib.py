#!/usr/bin/env python
from config import *
from lib import *
import time
import protocol_pb2
reload(sys)  
sys.setdefaultencoding('utf8')

# data
def normalizeData(companion,rd):
	for key in defaultProtocolSettings.keys():
		if hasattr(rd.meta, key):
			setattr(companion,key,getattr(rd.meta,key))
		else:
			if not hasattr(companion,key):
				setattr(companion,key,defaultProtocolSettings[key])
	companion.requestSize  = 0
	return companion, rd
def attachMeta(data):
	print ":attachMeta"
	data.meta.maxPostSize	= maxPostSize
	data.meta.maxRequestSize= maxRequestSize
	data.meta.acceptFiles	= acceptFiles
	data.meta.requiredPOW 	= requiredPOW
	data.meta.version 		= py2pVersion
	return data

#posts
def attachKnownPosts(data):
	global get
	print ":attachKnownPosts"
#		print get['received']
	for post in get['received']:
		print "		",post
		cur_post = data.known.add()
		cur_post.id = post
		cur_post.size = getPostSize(post)
		for tag in get["tags"][post]:
			cur_post.tags.append(tag)
		for language in get["languages"][post]:
			cur_post.languages.append(language)
	return data
def requestPosts(companion,data,rd):
	print ":requestPosts"
	for post in rd.known:
		print "		" ,post.id
		if not isReceived(post.id) and len(companion.toRequest) < maxToRequestListLength and not isDeleted(post.id) and checkLimits(companion,rd):
			companion.toRequest.add(post.id)
	toRemove = set()
	for postid in companion.toRequest:
		if not isReceived(postid) or isDeleted(postid):
			req = data.requesting.add()
			req.id = postid
			if companion.requestPOW != 0:
				req.pow , req.time= getRequestPOW(postid,companion.requestPOW)
				print "POW ",companion.requestPOW,"to request ",post.id," calculated"
		else:
			toRemove.add(postid)
	for item in toRemove:
		companion.toRequest.remove(item)
	return data

def sendPosts(companion,data,rd):
	print ":sendPosts"
	for requesting_post in rd.requesting:
		if checkRequestPOW(requesting_post,companion.requestPOW):
			if isReceived(requesting_post.id):
				if isAvaliable(requesting_post.id) and len(companion.toSend) < maxToSendListLength:
					companion.toSend.add(requesting_post.id)
	for postid in companion.toSend:
		if isAvaliable(postid):
			post = data.sending.add()
			post.ParseFromString(readFile(postsDir+postid))
			print "		[added to send]:",postid
		else:
			companion.toSend.remove(postid)
	return data
def receivePosts(rd):
	print ":receivePosts"
	for received_post in rd.sending:
		if not isDeleted(received_post.id) and not isReceived(received_post.id):
			print "		[new post received]:",received_post.id
			writePost(received_post)
	updateDB()

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
def checkLimits(companion,rd):
	r = False
	if companion.requestSize < rd.meta.maxRequestSize:
		r = True
	return r 
