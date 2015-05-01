#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import html
import urllib
from config import *
import time
import resource
from PIL import Image
import string
import protocol_pb2
reload(sys)  
sys.setdefaultencoding('utf8')

#constants
languagesList = ["en","ru","pol","uk","fr","de","fi","ja","lv","pol","es","sv"]
py2pVersion = 0
defaultProtocolSettings = {
	"maxPostsAtOnce": 100000,
	"maxPostSize": 5242880,
	"maxRequestSize": 104857600,
	"acceptFiles": True,
	"requestPOW": 0,
	"version": py2pVersion
}
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

#files
def createDirIfNotExists(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
def checkDirs():
	createDirIfNotExists(postsDir)
	createDirIfNotExists(postsFileDir)
	createDirIfNotExists(attachmentsDir)

def readFile(filename,mode="rb"):
	if fileExists(filename):
		fd = open(filename)
		content = fd.read()
		fd.close()
		return content
	else:
		return ""
def fileExists(filename):
	return os.path.isfile(filename)
def deleteFile(filename):
	os.remove(filename)
def getFileSize(filename):
	if fileExists(filename):
		return os.stat(filename).st_size
	else:
		return 0
def md5File(filename, blocksize=2**20):
	m = hashlib.md5()
	with open( os.path.join(filename) , "rb" ) as f:
		while True:
			buf = f.read(blocksize)
			if not buf:
				break
			m.update( buf )
	return m.hexdigest()
def md5(string):
	return hashlib.md5(string.encode("utf-8"))
#posts

def isReceived(postid):
	return fileExists(postsDir+postid)
def isDeleted(postid):
	return False
def isLocal(postid):
	return False
def isPostId(postid):
	return True
def getPostSize(postid):
	return getFileSize(postsDir+postid)
def readPost(postid):
	post = protocol_pb2.Post()
	if isReceived(postid):
		post.ParseFromString(readFile(postsDir+postid,'rb'))
	return post

def getFilePow(postid):
	post = readPost(postid)
	return getPostPow(post)
def getPostPow(post):
	post_content = stringifyPost(post)
	pid1 = str(hex2bin(md5(post_content+str(post.pow)).hexdigest()[2:]))
	pid2 = str(hex2bin(md5(str(post.pow)+post_content).hexdigest()[2:]))
	POW = 0
	while pid1[:POW] == pid2[:POW] and POW < 1000:
		POW+=1
	return POW-1

def stringifyPost(post):
	string = ""
	if hasattr(post, "name"):
		string += str(post.name)
	if hasattr(post, "subject"):
		string += str(post.subject)
	if hasattr(post, "text"):
		string += str(post.text)
	if hasattr(post, "time"):
		string += str(post.time)
	if hasattr(post, "files"):
		for file_entry in post.files:
			string += str(file_entry.md5hash)
	if hasattr(post, "tags"):
		for tag in post.tags:
			string += str(tag)
	if hasattr(post, "languages"):
		for lang in post.languages:
			string += str(lang)
	return string
def initDB():
	global get
	#post index
	get['connectedto'] = {}
	get['refersto'] = {}
	get['tags'] = {}
	get['languages'] = {}
	get['bytag'] = {}
	get['bylang'] = {}
	get['time'] = {}
	get['pow'] = {}
	get['servers'] = set()
	get['clients'] = {}
	get['files'] = {}
	get['byfilemd5hash'] = {}
	#peering
	get['servers'].add(Server().addHost("127.0.0.1:5441"))
	get['clients'] = {}

	#postmap
	get['received'] = set()
	get['deleted'] = set()
	updateDB()
	#get['initialized'] = True

def updateDB():
	global get, languagesList
	startTime = time.time()
	post_files = os.listdir(postsDir)	
	#print post_files
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
			if not hasattr( get['tags'], post.id):
				get['tags'][post.id] = set()
			get['tags'][post.id].add(tag)
		for lang in post.languages:

			if not post.id in get['languages']:
				get['languages'][post.id] = set()
			get['languages'][post.id].add(lang)

			if not lang in get['bylang'] and lang in languagesList:
				get['bylang'][lang] = set()
			get['bylang'][lang].add(post.id)
		for post_file in post.files:

			if not post.id in get['files']:
				get['files'][post.id] = set()
			get['files'][post.id].add(post_file.md5hash)

			if not post_file.md5hash in get['byfilemd5hash']:
				get['byfilemd5hash'][post_file.md5hash] = set()
			get['byfilemd5hash'][post_file.md5hash].add(post.id)
			file_ext = post_file.name.split(".")[len(post_file.name.split("."))-1]				
			if file_ext != "":
				file_name = postsFileDir+post_file.md5hash+"."+file_ext
			else:
				file_name =  postsFileDir+post_file.md5hash
			if not fileExists(file_name):
				fd = open(file_name,'wb')
				fd.write(post_file.source)
				fd.close()
				#print post.id ,"-> ", post_file.name
			else:
				do = "nothing"
				#print post.id ,"-[exitsts] ", post_file.name
		get['received'].add(post.id)
	endTime = time.time()
	print "Post parsing took ", float(endTime - startTime )
	print "Memory:",getMemUsage()

def deletePost(postid):
	if fileExists(postsDir+postid):
		post = protocol_pb2.Post()
		post.ParseFromString( readFile(postsDir + postid) )
		# removing files
		for post_file in post.files:
			if len(post_file.name.split("."))>1:
				file_ext = "."+post_file.name.split(".")[len(post_file.name.split("."))-1]
			else:
				file_ext = ""
			file_name =	post_file.md5hash+file_ext
			if post_file.md5hash in get['byfilemd5hash']:
				if post.id in get['byfilemd5hash'][post_file.md5hash]:
					get['byfilemd5hash'][post_file.md5hash].remove(post.id)
					if len(get['byfilemd5hash'][post_file.md5hash]) == 0:
						print "Deleting:", post.id
						del get['byfilemd5hash'][post_file.md5hash]
						if fileExists(postsFileDir+file_name):
							deleteFile(postsFileDir+file_name)
							print "removed attached file: " + file_name+" - "+post.id
						else:
							print "cannot remove attached file: "+file_name+" - "+post.id
	else:
		print "cannot delete post: ",post.id,"file not exists!"
	#removing tags 
	if post.id in get['tags']:
		tags = get['tags'][post.id]
		for tag in tags:
			if post.id in get['bytag'][tag]:
				get['bytag'][tag].remove(post.id)
				if len(get['bytag'][tag])==0:
					del get['bytag'][tag]
		del get['tags'][post.id]
	#removing languages
	if post.id in get['languages']:
		lengs = get['languages'][post.id]
		for lang in langs:
			if post.id in get['bylang'][lang]:
				get['bylang'][lang].remove(post.id)
				if len(get['bylang'][lang])==0:
					del get['bylang'][lang]
		del get['languages'][post.id]
	if post.id in get['connectedto']:
		del get['connectedto'][post.id]
	if post.id in get['refersto']:
		del get['refersto'][post.id]
	if post.id in get['time']:
		del get['time'][post.id]
	if post.id in get['files']:
		del get['files'][post.id]
	os.remove(postsDir+post.id)
	get['deleted'].add(post.id)

#math
def digit2char(digit):
	if digit < 10:
		return str(digit)
	return chr(ord('a') + digit - 10)

def hex2bin(shex):
	return bin(int(shex, 16))[2:]

def int36(n, b=36):
	digits = []
	while n:
		digits.append(int(n % b))
		n /= b
	digits = digits[::-1]
	r_string = ""
	for dig in digits:
		r_string += digit2char(dig)
	return r_string

#other
def getApproxTimeBySignatureLength(length):
	r = 1
	i = 0
	while i < length:
		i+=1
		r *= 2
	approxtime = r/100000
	return int(approxtime)

def getMemUsage():
	return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
def log(text):
	if loggingEnabled:
		if getFileSize(logFileName) < logMaxSize:
			fd = open(logFileName,"wa")
			fd.write(text)
			fd.close()
		print text
#classes

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
		self.refersto = ""
		self.connectedto = set()


class ValidatorClass():
	def hostname(self,hostname):
		if len(hostname) > 255:
			return False
		if hostname[-1] == ".":
			hostname = hostname[:-1] # strip exactly one dot from the right, if present
		allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
		return all(allowed.match(x) for x in hostname.split("."))
	def postid(self,postid):
		return True
	def tag(self,tag):
		return True
	def lang(self,lang):
		return lang in languagesList

class Server():
	def __init__(self,host="",port=0,ctype="client"):
		self.host = host
		self.port = port
		self.publicWebserverHost = ''
		self.total_accepted_connections = 0
		self.total_rejected_connections = 0
		self.rejected_connections = 0
		self.received_posts_count = 0
		self.received_posts_total_size = 0
	def addHost(self,host="127.0.0.1:5441"):
		host = host.split(":")
		port = host[1]
		host = host[0]
		self.host = host
		self.port = port
		return self

class Client():
	def __init__(self,host="",port=0):
		self.version = py2pVersion
		self.requestLengthLimit = 52428800 #50 MB
		self.maxPostSize = 5242880 # 5 MB
		self.maxPostsAtOnce = 100
		self.publicWebserverAddress = ''

		self.total_accepted_connections = 0
		self.total_rejected_connections = 0
		self.rejected_connections = 0
		
		self.requested_post_count = 0
		self.sent_post_count 	  = 0
	def addHost(self,host="127.0.0.1:5441"):
		host = host.split(":")
		port = host[1]
		host = host[0]
		self.host = host
		self.port = port
		return self


get = {}

valid = ValidatorClass()