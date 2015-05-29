#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import random
import math
import os
import sys
import html
import urllib
import re
import time
import resource
import string
import protocol_pb2
import protocol_pb2
import random
import math
from PIL import Image
from config import *
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto import Random

reload(sys) 
sys.setdefaultencoding('utf8')

#constants
languagesList = ["en","ru","pol","uk","fr","de","fi","ja","lv","pol","es","sv"]
py2pVersion = 0
n2 = {
	0:1,
	1:2,
	2:4,
	3:8,
	4:16,
	5:32,
	6:64,
	7:128,
	8:256,
	9:512,
	10:1024,
	11:2048,
	12:4096,
	13:8192,
	14:16384,
	15:32768,
	16:65536,
	17:131072,
	18:262144,
	19:524288,
	20:1048576,
	21:2097152,
	22:4194304,
	23:8388608,
	24:16777216,
	25:33554432,
	26:67108864,
	27:134217728,
	28:268435456,
	29:536870912,
	30:1073741824,
	31:2147483648,
	32:4294967296,
	33:8589934592,
	34:17179869184,
	35:34359738368,
	36:68719476736,
	37:137438953472,
	38:274877906944,
	39:549755813888
}
#logging
def R():
	print "--------------------------------------"
def log(message,level=1,indent=''):
	if indent == '':
		indent = {
			1:0,
			2:0,
			3:1,
			4:1,
			5:0
		}[level]
	indent = "										"[:indent]
	if level == 2:
		message = ":"+message
	if level in logSettings:
		print indent+message


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
		log("writeFile failed: "+filename, 5)
def fileExists(filename):
	return os.path.isfile(filename)
def deleteFile(filename):
	os.remove(filename)
def getFileSize(filename,dv=0):
	if fileExists(filename):
		return os.stat(filename).st_size
	else:
		return dv

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
def normalSize(bytesize):
	# 1024 -> 1KB
	pass


# cryptography

def genKeys1(address):
	global get
	kd = protocol_pb2.KeyExchange()
	kd.clientPublic = get['public_key']
	kd.serverPublic = get['public_keys'][address] = genKey()
	kd.clientSending = str(pow(int(kd.serverPublic),int(get['private_key']),int(kd.clientPublic)))
	return kd.SerializeToString()+keyExchangeMessageDetector

def genKeys2(data,address):
	global get
	rd = protocol_pb2.KeyExchange()
	rd.ParseFromString(data)
	get['shared_keys'][address] = string2key(str(pow(int(rd.clientSending),int(get['private_key']),int(rd.clientPublic))))
#	print "SHARED KEY = ",get['shared_keys'][address]
	kd = protocol_pb2.KeyExchange()
	kd.serverSending = str(pow(int(rd.serverPublic),int(get['private_key']),int(rd.clientPublic))%int(rd.clientPublic))
	return kd.SerializeToString()

def genKeys3(data,address):
	global get
	rd = protocol_pb2.KeyExchange()
	rd.ParseFromString(data)
	get['shared_keys'][address] = string2key(str(pow(int(rd.serverSending),int(get['private_key']),int(get['public_key']))))
#	print "SHARED KEY = ",get['shared_keys'][address]

def padAES(s):
	numpads = 16 - (len(s)%16)
	return s + numpads*chr(numpads)

def stripAES(s):
	if len(s)%16 or not s:
		raise ValueError("String of len %d can't be PCKS7-padded" % len(s))
	numpads = ord(s[-1])
	if numpads > 16:
		raise ValueError("String ending with %r can't be PCKS7-padded" % s[-1])
	return s[:-numpads]

def encodeAES(data,key):
	encobj = AES.new(key, AES.MODE_ECB)
	data = padAES(data)
	ciphertext = encobj.encrypt(data)
	return ciphertext
def decodeAES(data,key):
	decobj = AES.new(key, AES.MODE_ECB)
	plaintext = decobj.decrypt(data)
	plaintext = stripAES(plaintext)
	return plaintext
def string2key(string):
	r = ''
	s = md5digest(string)[:16]
	s+= md5digest(string+s+r)[:16]
	s+= md5digest(string+s+r)[:16]
	s+= md5digest(string+s+r)[:16]
#	print len(s), s
	i = 0
	while i < 64:
		r += chr(int(s[i:][:2],16))
		i+=2
#	print r,len(r)
	return r
def genKey():
	a = int(os.urandom(keyLength/8).encode('hex'),16)
	return str(a)
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
def md5digest(source):
	return hashlib.md5(source.encode("utf-8")).hexdigest()
#posts
def isReceived(postid):
	return fileExists(postsDir+postid)
def isDeleted(postid):
	return False
def isTree(postid):
	if postid in get['connected']:
		for reply in get['connected'][postid]:
			if isThread(reply):
				return True
	return False
def isThread(postid):
	if postid in get['connected']:
		if len(get['connected'][postid]) > 0:
			return True
	return False
def isAvaliable(postid):
	return not isDeleted(postid) and not isLocal(postid) and isReceived(postid)
def isLocal(postid):
	# deprecated?
	return False
def isPostId(postid):
	return True
def getPostSize(postid,dr = maxPostSize):
	global get
	if not postid in get['postsize']:
		get['postsize'][postid] = getFileSize(postsDir+postid)
	return get['postsize'][postid]
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
def getFilePOW(postid):
	post = readPost(postid)
	return getPostPOW(post)
def getPostPOW(post):
	if hasattr(post,'id'):
		post_content = stringifyPost(post)
	else:
		post = readPost(post)
		post_content = stringifyPost( post)
	pid1 = str(hex2bin(md5digest(post_content+str(post.pow))))
	pid2 = str(hex2bin(md5digest(str(post.pow)+post_content)))
	POW = 0
	while pid1[:POW] == pid2[:POW] and POW < 1000:
		POW+=1
	return POW-1

def stringifyPost(post):
	string = ""
	if hasattr(post, "refer"):
		string += str(post.refer)
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

def checkPost(post):
	if not hasattr(post,"id") or not isPostId( post.id ):
		return 1
	if not hasattr(post, "time"):
		return 1
	if not checkTime(post.time):
		return 1
	if getPostPOW(post) < minPostPOW:
		return 2
	if hasattr(post, "tags"):
		if not checkTags(post.tags):
			return 3
	if hasattr(post, "text"):
		if not checkText(post.text):
			return 3
	if hasattr(post, "files"):
		if not checkFiles(post.files):
			return 4
	return 0

def checkTime(posttime):
	return toInt(posttime,0) < time.time()*10000 + timeShift
def checkTags(posttags):
	for tag in posttags:
		if tag in bannedTags:
			return False
	return True
def checkText(post):
	for banned in bannedWords:
		if hasattr(post,"text"):
			if post.text.find(banned) != -1:
				return False
		if hasattr(post,"name"):
			if post.name.find(banned) != -1:
				return False
		if hasattr(post, "subject"):
			if post.subject.find(banned) != -1:
				return False
	return True
def checkFiles(postfiles):
	for file_entry in postfiles:
		if hasattr(file_entry,"name") and \
			hasattr(file_entry,"source") and \
			hasattr(file_entry,"md5hash"):
			if md5source( file_entry.source ) != file_entry.md5hash:
				return False
	return True

def loadAdministration():
	if fileExists(administrationFile):
		admins = protocol_pb2.BoardAdministration()
		admins.ParseFromString(readFile(administrationFile))
		if len(admins.list):
			log("Administration: ")
			for admin in admins.list:
				log("	- "+admin.name)
				get['admins'][admin.name] = {
					"passwordmd5": admin.passwordmd5,
					"modsigning": admin.modsigning,
					"modsign": admin.modsign,
					"deleting": admin.deleting
				}
		else:
			log("[WARNING] no administrator profile set",4)
			log("Use adduser.py to add administrators and moderators",4)
def loadProtectedPosts():
	global get
	#log("loadProtectedPosts",2)
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
		p.id = postid
		p.timebonus = timebonus
		p.modhtml = modhtml
		p.modname = modname
		p.sticked = sticked
		saveProtectedPosts()

def updateDB():
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
	log("Post parsing took "+str(float(endTime - startTime )),1)
	log("Memory:"+str(getMemUsage()),1)
	return new_posts,removed_posts
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
			log(post.id +" -> "+ post_file.name,2)
		else:
			do = "nothing"
			#print post.id ,"-[exitsts] ", post_file.name

	get['timestamp'][post.id] = post.time
	get['pow'][post.id] = getPostPOW(post)
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
	if fileExists(webServerPostsDir+postid):
		os.remove(webServerPostsDir+postid)
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

def hashesCount(POW):
	POW = toInt(POW,0)
	if POW in n2:
		return n2[POW]
	else:
		return 0
def POWBonus(postid,recursionValue=0):
	r = 0
	if postDeletingMode == "progressive":
		if recursionValue >= 10:
			return 0
		if postid in get['timestamp']:
			if postid in get['pow']:
				if postid in get['connected']:
					r += get['pow'][postid]*hashesCount(get['pow'][postid])*powInfluence + POWBonus(get['connected'][postid], recursionValue +1)
				else:
					r = get['pow'][postid]*hashesCount(get['pow'][postid])*powInfluence
	return r
def cutOutdatedPosts():
	log(":cutOutdatedPosts",2)
	if maxPostsCount != 0:
		if len(get['received']) > maxPostsCount:
			post_rating = {}
			to_delete = []
			if postDeletingMode == "progressive":
				for postid in get['received']:
					if( postid in get['refer'] and not isReceived(get['refer'][postid]) ) or \
					not postid in get['refer']:
						post_rating[postid] = toInt(get['timestamp'][postid],0)
						post_rating[postid] += POWBonus(postid)
				sorted_post_rating = sorted(post_rating, key=post_rating.__getitem__,reverse=False)
				deleted_counter = 0
				delete_count = len(get['received']) - maxPostsCount
				for postid in sorted_post_rating:
					log("cutOutdatedPosts: "+postid+":",post_rating[postid],3)
					deletePost(postid)
					deleted_counter+=1
					if deleted_counter >= delete_count:
						break


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
	get['postsize'] = {}
	get['filecache'] = {}
	get['clients'] = {}
	get['public_key'] = genKey()
	get['private_key'] = genKey()
	get['public_keys'] = {}
	get['shared_keys'] = {}
	#postmap
	get['received'] = set()
	get['deleted'] = set()

	get['admins'] = {}
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
	log( "loadServers",2)
	get['servers'] = protocol_pb2.ServersList()
	try:
		get['servers'].ParseFromString(readFile(serversListFile))
	except BaseException:
		log(":loadServers: [warning] cannot load servers list! ("+serversListFile+") (using default one)",4)
		try:
			get['servers'].ParseFromString(readFile(defaultServersListFile))
		except BaseException:
			log(":loadServers: [error] cannot load default servers list! ("+defaultServersListFile+") (exiting)",5)
			sys.exit(0)
	for server in get['servers'].list:
		log("Adress: "+server.address+" received posts:"+str(server.received),3)
		server.rejected = 0
		if not hasattr(server,"address"):
			server.address = "127.0.0.1;5441"
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
#other

def get_class_members(klass): # <- for debug
	ret = dir(klass)
	if hasattr(klass,'__bases__'):
		for base in klass.__bases__:
			ret = ret + get_class_members(base)
	return ret


def uniq( seq ): 
	""" the 'set()' way ( use dict when there's no set ) """
	return list(set(seq))

def get_object_attrs( obj ):
	ret = dir( obj )

	if hasattr( obj, '__class__'):
		ret.append('__class__')
		ret.extend( get_class_members(obj.__class__) )
		ret = uniq( ret )
	return ret

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
		tag = tag.replace("/","").replace("#","").replace(",","")
		tag = tag.strip()
		return tag
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

get = {}
valid = ValidatorClass()