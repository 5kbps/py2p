#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import html
import urllib
import re
from config import *
from base64 import b64decode
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
def R():
	print "--------------------------------------"
#lists
def get_class_members(klass):
    ret = dir(klass)
    if hasattr(klass,'__bases__'):
        for base in klass.__bases__:
            ret = ret + get_class_members(base)
    return ret


def uniq( seq ): 
    """ the 'set()' way ( use dict when there's no set ) """
    return list(set(seq))

def get_object_attrs( obj ):
    # code borrowed from the rlcompleter module ( see the code for Completer::attr_matches() )
    ret = dir( obj )
    ## if "__builtins__" in ret:
    ##    ret.remove("__builtins__")

    if hasattr( obj, '__class__'):
        ret.append('__class__')
        ret.extend( get_class_members(obj.__class__) )

        ret = uniq( ret )

    return ret

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
def getExt(filename):
	if filename.find(".")!=-1:
		return filename.split(".")[len(filename.split("."))-1]
	else:
		return ""
def checkDirs():
	createDirIfNotExists(postsDir)
	createDirIfNotExists(postsFileDir)
	createDirIfNotExists(attachmentsDir)
	createDirIfNotExists(webServerDir)
	createDirIfNotExists(webServerPostsDir)
	createDirIfNotExists(webServerThreadsDir)
	createDirIfNotExists(webServerImageThumbDir)
	createDirIfNotExists("meta")

def readFile(filename,mode="rb"):
	if fileExists(filename):
		fd = open(filename)
		content = fd.read()
		fd.close()
		return content
	else:
		return ""
def writeFile(filename,content,mode="wb"):
	try:
		fd = open(filename,mode)
		fd.write(content)
		fd.close()
	except BaseException as e:
		print "		:writeFile failed", e
		pass
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
				f.close()
				break
			m.update( buf )
	return m.hexdigest()
def md5(string,noUTF=False):
	if not noUTF:
		return hashlib.md5(string.encode("utf-8"))
	else:
		return hashlib.md5(string)
def md5source(source):
	m = hashlib.md5()
	i = 0
	l = 2**20
	cl = len(source)
	while  True:
		m.update(source[i*l:][:l])
		if l*i>=cl:
			break
		else:
			i+=1
	return m.hexdigest()
#posts
def isReceived(postid):
	return fileExists(postsDir+postid)
def isDeleted(postid):
	return False
def isAvaliable(postid):
	return not isDeleted(postid) and not isLocal(postid) and isReceived(postid)
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
def writePost(post):
	if post.id:
		fd = open(postsDir+post.id,'w')
		fd.write(post.SerializeToString())
		fd.close()
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
			string += str(file_entry.name)
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
	get['connected'] = {}
	get['refer'] = {}
	get['tags'] = {}
	get['languages'] = {}
	get['bytag'] = {}
	get['bylang'] = {}
	get['timestamp'] = {}
	get['pow'] = {}
	get['companions'] = {}
	get['files'] = {}
	get['byfilemd5hash'] = {}
	get['requesting'] = {}
	get['pow'] = {}
	#peering
	get['clients'] = {}
	#postmap
	get['received'] = set()
	get['deleted'] = set()

	updateDB()
	loadServers()
#	loadServers()
#	addServer("127.0.0.1:5441")
	#get['initialized'] = True


def addServer(address):
	global get
	server = get['servers'].list.add()
	server.address = address
	server.rejected = 0
	server.received = 0
	server.new = True

def loadServers():
	global get
	print "		:loadServers"
	get['servers'] = protocol_pb2.ServersList()
	try:
		get['servers'].ParseFromString(readFile(serversListFile))
	except BaseException:
		print "		:loadServers: [warning] cannot load servers list! ("+serversListFile+") (using default one)"
		try:
			get['servers'].ParseFromString(readFile(defaultServersListFile))
		except BaseException:
			print "		:loadServers: [error] cannot load default servers list! ("+defaultServersListFile+") (exiting)"
			sys.exit(0)
	for server in get['servers'].list:
		server.rejected = 0
		if not hasattr(server,"address"):
			server.address = "127.0.0.1;5441"
		if not hasattr(server,"received"):
			server.received = 0
		if not hasattr(server,"received"):
			server.received = 0
def saveServers():
	writeFile(serversListFile,get['servers'].SerializeToString())
def getServerList():
	global get
	r = []
	for s in get['servers'].list:
		if hasattr(s,"address"):
			r.append(s.address)
	return r
def updateDB(callback = 0):
	global get
	startTime = time.time()
	post_files = set(os.listdir(postsDir))
	known_posts =get['received']
	new_posts 		= post_files - known_posts
	removed_posts   = known_posts- post_files

	for postid in new_posts:
		add2DB(postid)
	for postid in removed_posts:
		purgePost(postid)
	endTime = time.time()
	loadProtectedPosts()
	print "Post parsing took ", float(endTime - startTime )
	print "Memory:",getMemUsage()

def loadProtectedPosts():
	global get
#	print ":loadProtectedPosts"
	protected = protocol_pb2.ProtectedPosts() 
	protected.ParseFromString(readFile(protectedPostsFile,"r"))
	get['protected'] = protected.list

def saveProtectedPosts():
	global get
	protected = protocol_pb2.ProtectedPosts()
	protected.list = get['protected']
	writeFile(protectedPostsFile,protected.SerializeToString(),'w')

def addProtectedPost(postid,timebonus=-1,modhtml=defaultAdminSign,modname=defaultAdminName, sticked=False,callback=0):
	if isReceived(postid):
		p = get['protected'].add()
		p.timebonus = timebonus
		p.modhtml = modhtml
		p.modname = modname
		p.sticked = sticked
		saveProtectedPosts()

def add2DB(postid):
	post = readPost(postid)
	# referrers
	if hasattr( post, "refer"):
		if isReceived(post.refer):
			if not post.refer in get['connected']:
				get['connected'][post.refer] = set()
			get['connected'][post.refer].add( post.id)
			if not post.id in get['refer']:
				get['refer'][post.id] = post.refer
	#tags
	for tag in post.tags:
		if not tag in get['bytag']:
			get['bytag'][tag] = set()
		get['bytag'][tag].add(post.id)
		if not hasattr( get['tags'], post.id):
			get['tags'][post.id] = set()
		get['tags'][post.id].add(tag)
	#languages
	for lang in post.languages:
		if not post.id in get['languages']:
			get['languages'][post.id] = set()
		get['languages'][post.id].add(lang)

		if not lang in get['bylang'] and lang in languagesList:
			get['bylang'][lang] = set()
		get['bylang'][lang].add(post.id)
	#files
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

	get['timestamp'][post.id] = post.time
	get['pow'][post.id] = getPostPow(post)
	get['received'].add(post.id)

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
						#remove main file
						if fileExists(postsFileDir+file_name):
							deleteFile(postsFileDir+file_name)
							print "removed attached file: " + file_name+" - "+post.id
						#remove thumbnail
						if fileExists(webServerImageThumbDir+post_file.md5hash+".jpg"):
							deleteFile(webServerImageThumbDir+post_file.md5hash+".jpg")
						else:
							print "cannot remove attached file: "+file_name+" - "+post.id
		os.remove(postsDir+postid)
		get['deleted'].add(postid)
	else:
		print "cannot delete post: ",postid,"file not exists!"
	purgePost(postid)

def purgePost(postid):
	#removing tags 
	if postid in get['tags']:
		tags = get['tags'][postid]
		for tag in tags:
			if postid in get['bytag'][tag]:
				get['bytag'][tag].remove(postid)
				if len(get['bytag'][tag])==0:
					del get['bytag'][tag]
		del get['tags'][postid]
	#removing languages
	if postid in get['languages']:
		langs = get['languages'][postid]
		for lang in langs:
			if postid in get['bylang'][lang]:
				get['bylang'][lang].remove(postid)
				if len(get['bylang'][lang])==0:
					del get['bylang'][lang]
		del get['languages'][postid]
	if postid in get['connected']:
		del get['connected'][postid]
	if postid in get['refer']:
		del get['refer'][postid]
	if postid in get['timestamp']:
		del get['timestamp'][postid]
	if postid in get['pow']:
		del get['pow'][postid]
	if postid in get['files']:
		del get['files'][postid]
	if postid in get['protected']:
		del get['protected'][postid]

def cutPosts():
	# to delete posts if their count is more than maximum
	pass
#math
def toInt(string,default=0):
	try:
		return int(string)
	except BaseException:
		return default
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
	def base64URL(self,url):
		return b64decode(url[url.find("base64,")+7:])
	def hostname(self,hostname):
		if not hostname:
			return False
		if len(hostname) > 255:
			return False
		if hostname[-1] == ".":
			hostname = hostname[:-1] # strip exactly one dot from the right, if present
		allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
		return all(allowed.match(x) for x in hostname.split("."))

"""
class Server():
	def __init__(self,host="",port=0,ctype="client"):
		self.host = host
		self.port = port
		self.publicWebserverHost = ''
		self.total_accepted_connections = 0
		self.total_rejected_connections = 0
		self.failed = 0
		self.rejected_connections = 0
		self.received_posts_count = 0
		self.received_posts_total_size = 0

	def addHost(self,host="127.0.0.1:5441"):
		global get
		get['hostlist'].add(host.replace("\n",""))
		host = host.split(":")
		port = host[1]
		host = host[0]
		self.host = host
		self.port = port
		return self
"""

get = {}

valid = ValidatorClass()

#initDB()
#updateDB()
#print get
