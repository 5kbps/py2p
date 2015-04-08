#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from hashlib import md5
from base64 import b64encode
import urllib
import time
import socket
import protocol_pb2
from lib import datop, valid
from lib import *

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

def CreatePost(name=newPostDefaultName,subject=newPostDefaultSubject,text="",files=newPostDefaultFiles,tags=newPostDefaultTags,refersto=0,languages=newPostDefaultLanguages,signature_length=newPostDefaultSignatureLength):
	###
	curtime = int(time.time()*10000)
	post = protocol_pb2.Post()
	post.name = name
	post.subject = subject
	post.text = text
	post.time = curtime
	if files != "":
		file_list = string2list(files)	
		print file_list
		for f in file_list:
			if valid.fileExists(attachmentsDir+ f):
				fo = post.files.add()
				fo.name = f
				fo.source = readFile(attachmentsDir+ f,'rb')
	tag_list = trimStringAsList(tags)
	for tag in tag_list:
		if valid.tag(tag):
			to = post.tags.add()
			to = tag
	languages_list = trimStringAsList(languages)
	for lang in languages_list:
		if valid.lang(lang):
			lo = post.languages.add()
			lo = lang
	connectedto =""
	sig_shift = 0
	print "Generating \"proof of work\" signature. It can take some time (approximately "+str(getApproxTimeBySignatureLength(int(signature_length)))+"s)"
	starttime = int(time.time()*1000000)
	post_content = name+subject+text+str(curtime)+tags
	while True:
		id = md5((name+subject+text+str(curtime)+str(sig_shift)+tags+languages+refersto).encode('utf-8')).hexdigest()[2:]
		tid =md5((id+str(sig_shift)).encode('utf-8')).hexdigest()[2:]
		id2 = hex2bin(id)
		tid2= hex2bin(tid)
		if str(id2)[:signature_length] == str(tid2)[:signature_length]:
			break
		else:
			sig_shift+=1
	endtime = int(time.time()*1000000)
	post.id = id
	postFileText = post.SerializeToString()
	#writing to file
	fd = open(postsDir+str(datop.int36(int(id,16))),'w')
	fd.write(postFileText)
	fd.close()
	# adding connectedto links
	#for postid in refersto_list:
	#	lib.addPostConnectedTo(postid,id)

	print("Post with id "+id+" created. [singature length: {TODO}, time = "+str((endtime-starttime)/1000000)+"s, "+str(sig_shift*2)+" hashes] ")

name = raw_input("Name: ")
subject = raw_input("Subject: ")
text = raw_input("Text: ")
files = raw_input("Attached files (comma separated) (put files in "+os.getcwd()+"/"+attachmentsDir+" folder first): ")
tags = raw_input("Tags (comma separated): ")
languages = "ru,en"
refersto = raw_input("Insert links to other posts to make an answer (comma separated): ")
siglen = raw_input("Sugnature length (0-25): ")
if siglen == "":
	siglen = newPostDefaultSignatureLength
if files=="":
	files = newPostDefaultFiles
np = CreatePost(name,subject,text,files,tags,refersto,"en,ru",siglen)
