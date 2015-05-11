#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sys
from hashlib import md5
from base64 import b64encode
import urllib
import time
import socket
import protocol_pb2
from lib import *

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

def CreatePost(name=newPostDefaultName,subject=newPostDefaultSubject,text="",files='',tags='',refersto=0,languages=newPostDefaultLanguages,minimumPow=newPostDefaultPOW):
	###
	current_time = int(time.time()*10000)
	post = protocol_pb2.Post()
	post.name = unicode(name.strip())
	post.subject = unicode(subject.strip())
	post.text = unicode(text.strip())
	post.time = str(current_time)
	if files == '':
		file_list = newPostDefaultFiles
	else:
		file_list = string2list(files)
		for f in file_list:
			if fileExists(attachmentsDir+ f):
				fo = post.files.add()
				fo.name = f
				fo.md5hash = md5File(attachmentsDir + f)
				#fo.source = b64encode(readFile(attachmentsDir+ f,'r'))
				fo.source = readFile(attachmentsDir+ f,'r')
	tag_list = string2list(unicode(tags))
	languages_list = string2list(unicode(languages))
	for tag in tag_list:
		if valid.tag(tag):
			to = post.tags.append(tag)
	for lang in languages_list:
		if valid.lang(lang):
			lo = post.languages.append(lang)
	post.refer = refersto.strip()
	if getApproxTimeBySignatureLength(int(minimumPow)) > 3:
		print "Generating \"proof of work\" signature. It can take some time (approximately "+str(getApproxTimeBySignatureLength(int(minimumPow)))+"s)..."
	start_time = int(time.time()*1000000)
	post_content = stringifyPost(post)
	pow_shift = 0
	while True:
		id = md5(post_content+str(pow_shift)).hexdigest()[2:]
		tid =md5(str(pow_shift)+post_content).hexdigest()[2:]
		id2 = hex2bin(id)
		tid2= hex2bin(tid)
		if str(id2)[:minimumPow] == str(tid2)[:minimumPow]:
			break
		else:
			pow_shift+=1
	endtime = int(time.time()*1000000)
	post.pow = pow_shift
	post.id = int36(int(id,16))
	postFileText = post.SerializeToString()
	#writing to file
	fd = open(postsDir+str(int36(int(id,16))),'wb')
	fd.write(postFileText)
	fd.close()
#	si.parsePosts()
	# adding connectedto links
	#for postid in refersto_list:
	#	lib.addPostConnectedTo(postid,id)
	print("Post with id "+id+" created. [POW: "+str(getFilePow(post.id))+" = "+str(getPostPow(post))+", time: "+str((endtime-start_time)/1000)+"ms, hashes: "+str(pow_shift*2)+"] ")


if "--test" in sys.argv:
	for i in range(1,20):
		np = CreatePost("name","subject","text","test.jpg","o,tag,test","","en,ru",3)
else:
	name = raw_input("Name: ")
	subject = raw_input("Subject: ")
	text = raw_input("Text: ")
	files = raw_input("Attached files (comma separated) (put files in "+os.getcwd()+"/"+attachmentsDir+" folder first): ")
	tags = raw_input("Tags (comma separated): ")
	languages = "ru,en"
	refersto = raw_input("Insert links to other posts to make an answer (comma separated): ")
	POW = raw_input("Sugnature length (0-25): ")
	if POW == "":
		POW = newPostDefaultPOW
	else:
		POW = int(POW)

	np = CreatePost(name,subject,text,files,tags,refersto,"en,ru",POW)