#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import hashlib
import base64
import os
import sys
import html
import urllib
import os
from config import *
import time
from xml.sax.saxutils import escape, unescape
import datetime
import operator
import struct
from PIL import Image
from config import *
import resource
import setproctitle
import string
import shelve
from Crypto.Cipher import AES
import protocol_pb2
reload(sys)  
sys.setdefaultencoding('utf8')

"""
pbPost = protocol_pb2.Post()
pbPost.id = "12345"
pbPost.name = "IVAN"
pbPost2 = protocol_pb2.Post()
fd = open("fd",'w')
fd.write(pbPost.SerializeToString())
fd.close()
pbPost2.ParseFromString(pbPost.SerializeToString())
print pbPost2.id
"""
#lists
def trimStringAsList(string):
	string = removeEmptyItems( string.split(","))
	string = removeEmptyItems(string)
	string = ",".join(string)
	return string
def string2list(string,separator=","):
	return removeEmptyItems(string.split(separator))
def removeEmptyItems(liste):
	liste = filter(None, liste)
	return liste


#other
def getApproxTimeBySignatureLength(length):
	r = 1
	i = 0
	while i < length:
		i+=1
		r *= 2
	approxtime = r/100000
	return int(approxtime)

class MemoryControlClass:
	def getMemUsage():
		return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

class SerializatorClass:
	def serializePost(self,postid):
		do = "nothing"

class Serializator():
	def serializePost(self,post,attachFile = True):
		serialized = protocol_pb2.Post()
		serialized.id = post.id
		serialized.name = post.name
		serialized.subject = post.subject  
		serialized.text = post.text
		serialized.time = post.time
		serialized.signature = post.signature
		serialized.filename = post.filename
		if attachFile == True and validator.fileExists(postsFileDir+post.filename):
			fd = open(postsFileDir+post.filename)
			serialized.file = fd.read()
			fd.close()
		serialized.file = post.fileName
		return serialized.SerializeToString()

class DataOperator:
	def padAES(self,data):
		print "L::::",data
		return data + (32 - len(data) % 32) * " "
	def EncodeAES(self,data,key):
		cipher = AES.new(self.padAES(key))
		return cipher.encrypt(self.padAES(data))
	def DecodeAES(self,data,key):
		cipher = AES.new(self.padAES(key))
		return cipher.decrypt(self.padAES(data)).rstrip(" ")
	def base64Encode(self,string):
		return base64.b64encode(string)
	def base64Decode(self,string):
		try:
			return	base64.b64decode(string)
		except TypeError as e:
			log("error when b64 decoding:")
			print e
			return ""
	def getFileHash(self,filename, blocksize=2**20):
		m = hashlib.md5()
		with open( os.path.join(filename) , "rb" ) as f:
			while True:
				buf = f.read(blocksize)
				if not buf:
					break
				m.update( buf )
		return m.hexdigest()
	def genKey(self):
		return int(os.urandom(clientPrivateKeyLength).encode('hex'),16)
	def digit2char(self,digit):
		if digit < 10:
			return str(digit)
		return chr(ord('a') + digit - 10)
	def int36(self,n, b=36):
		digits = []
		while n:
			digits.append(int(n % b))
			n /= b
		digits = digits[::-1]
		r_string = ""
		for dig in digits:
			r_string += self.digit2char(dig)
		return r_string
	def safeSplit(string,separator=",",index="none",default = ""):
		r_list = string.split(separator)
		if len(r_list) > index:
			if index == "none":
				return r_list
			else:
				return r_list[index]
		else:
			return default
	def parseInt(self,integer):
		return int(integer)
	def bool(self,string):
		if string in ["1","True","true"]:
			return True
		else:
			return False
def hex2bin(shex):
	return bin(int(shex, 16))[2:]

class PostClass:
	def __init__(self):
		self.id = ''
		self.name = ''
		self.subject = ''
		self.text = ''
		self.time = 0
		self.signature = 0
		self.siglen = 0
		self.fileName = ''
		self.tags = set()
		self.languages = set()
		self.refersto = ()
		self.connectedto = ()


class ValidatorClass():
	def isHostname(self,hostname):
		if len(hostname) > 255:
			return False
		if hostname[-1] == ".":
			hostname = hostname[:-1] # strip exactly one dot from the right, if present
		allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
		return all(allowed.match(x) for x in hostname.split("."))
	def isPostId(self,postid):
		return True
	def key(self,public_key):
		return True
	def fileExists(self,fname):
		return os.path.isfile(fname)
	def tag(self,tag):
		#validate tag
		return True
	def lang(self,lang):
		return lang in ["ru","en","de","fr","bl"]

class CompanionClass():
	def __init__(self,host="",port=0,ctype="client"):
		self.host = host
		self.port = port
		self.version = "0.1.1"
		self.type = ctype
		self.is_public = False
		self.listening_on_host = ''
		self.listening_on_port = 0
		self.request_length_limit = 52428800 #50 MB
		self.accepts_images = True
		self.max_post_size = 5242880 # 5 MB
		self.public_webserver_port = ''
		self.public_webserver_host = ''
		self.total_accepted_connections = 0
		self.total_rejected_connections = 0
		self.rejected_connections = 0
		self.clientKey = 0#int(os.urandom(clientPrivateKeyLength).encode('hex'),16)
		self.serverKey = 0#int(os.urandom(clientPublicKeyLength).encode('hex'),16)
		self.sendingKey = 0
		self.receivedKey = 0
		self.secretKey = 0
		self.sharedKey = 0
		
	def addHost(self,host="127.0.0.1:5441"):
		host = host.split(":")
		port = host[1]
		host = host[0]
		self.host = host
		self.port = port
		return self
class UI:
	def log(self,text):
		print text

class ShelveInterface:
	def __init__(self):
		self.load()
	def defaults(self):
		global get
		get['connectedto'] = {}
		get['refersto'] = {}
		get['tags'] = {}
		get['bytag'] = {}
		get['bylang'] = {}
		get['time'] = {}
		get['siglen'] = 0
		get['hosts'] = set()
		get['clients'] = {}
		#get['hosts'].add(CompanionClass().addHost("a-chan.org:5441"))
		get['hosts'].add(CompanionClass().addHost("127.0.0.1:5441"))

		get['received'] = set()
		get['requesting'] = set()
		get['deleted'] = set()
		get['initialized'] = True
		self.parsePosts()

	def parsePosts(self):
		post_files = os.listdir(postsDir)	
		print post_files
		for post_file in post_files:
			post = protocol_pb2.Post()
			post.ParseFromString( readFile(postsDir+ post_file) )
			if hasattr( post, "refersto"):
				if not post.refersto in get['connectedto']:
					get['connectedto'][post.refersto] = set()
				get['connectedto'][post.refersto].add( post.id)
			if hasattr(post, "refersto"):
				if not post.id in get['refersto']:
					get['refersto'][post.id] = post.refersto
			for tag in post.tags:
				if not tag in get['bytag']:
					get['bytag'][tag] = set()
				get['bytag'][tag].add(post.id)
			for lang in post.languages:
				if not lang in get['bylang']:
					get['bylang'][lang] = set()
				get['bylang'][lang].add(post.id)
	def load(self):
		global get
		get = shelve.open(shelveFileName, writeback=True)
		if not "initialized" in get:
			self.defaults()
			print "Database generated"
	def save(self):
		global get
		get.sync()
	def close(self):
		global get
		get.close()

class StringifyClass:
	def receivedPosts(self):
		global get, validator
		return_string = ""
		post_list = get['received']
		for post in post_list:
			if validator.isPostId(post.id):
				return_string += post.id
		return return_string
	def flags(self):
		return_string = ""
		return_string += str(clientVersion)+":"
		return_string += str(int(clientIsPublic))+":"
		return_string += str(clientListeningOnHost)+":"
		return_string += str(clientListeningOnPort)+":"
		return_string += str(clientRequestLengthLimit)+":"
		return_string += str(int(clientAcceptImages))+":"
		return_string += str(clientMaxPostSize)+":"
		return_string += str(clientPublicWebserverHost)+":"
		return_string += str(int(clientPublicWebserverPort))
		return return_string

class ParserClass:
	def parseKey(self,key):
		return long(key)
	def flags(self,string):
		return_companion = CompanionClass()
		return_companion.version = safeSplit(string=string, separator=":",index=0)
		return_companion.is_public = charoperator.bool(safeSplit(string=string, separator=":",index=1))
		return_companion.listening_on_host = safeSplit(string=string, separator=":",index=0)
		return_companion.listening_on_port = charoperator.parseInt( safeSplit(string=string, separator=":",index=0))
		return_companion.request_length_limit = charoperator.parseInt( safeSplit(string=string, separator=":",index=0))
		return_companion.max_post_size = charoperator.parseInt( safeSplit(string=string, separator=":",index=0))
		return_companion.accepts_images = charoperator.bool( safeSplit(string=string, separator=":",index=0))
		return_companion.public_webserver_host = safeSplit(string=string, separator=":",index=0)
		return_companion.public_webserver_port = charoperator.parseInt( safeSplit(string=string, separator=":",index=0))

class ErrorKeys():
	def getTextByCode(self,code):
		if code == 301:
			return "You public key is not valid."
		if code == 302:
			return "Public key that you send is not valid."
		if code == 303:
			return "Computed key that you send is not valid."
		if code == 302:
			return "Public key that you send is not valid."
		if code == 302:
			return "Public key that you send is not valid."
		if code == 302:
			return "Public key that you send is not valid."
		

def readFile(filename,mod='r'):
	fd = open(filename,mod)
	source=fd.read()
	fd.close()
	return source


"""
clientIsPublic = False
clientListeningOnHost = ""
clientListeningOnPort = 0
clientRequestLengthLimit = 52428800 # 50 MB
clientAcceptImages = True
clientMaxPostSize = 5242880
clientPublicWebserverHost = ""
clientPublicWebserverPort
"""


strfy = StringifyClass()
valid = ValidatorClass()
datop = DataOperator()
parser = ParserClass()
ui = UI()
get = None
si = ShelveInterface()

#print "List of known hosts: "

"""for companion in get['hosts']:
	print "   " ,companion.host, companion.port
"""
#print stringify.flags()
