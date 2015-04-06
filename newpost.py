#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import hashlib
import base64
import urllib
import time
import socket
import lib

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

def b64String(string):
	return base64.b64encode(string)
###
"""

def NewPost(name,subject,text,imagePath,tags,refersto,languages,signature_length):
	name = name
	subject = subject
	text = text
	imageBase64 = b64Image(imagePath)
	imageBase64 = imagePath[-3:]+","+imageBase64
	curtime = int(time.time()*10000)
	tags = lib.trimStringAsList(tags)
	refersto = lib.trimStringAsList(refersto)
	languages = lib.trimStringAsList(languages)
	connectedto =""
	sig_shift = 0
	print "Generating \"proof of work\" signature. It can take some time (approximately "+str(lib.getApproxTimeBySignatureLength(signature_length))+"s)"
	starttime = int(time.time()*1000000)
	while True:	
		id = hashlib.md5((name+subject+text+str(curtime)+str(sig_shift)+tags+languages+refersto).encode('utf-8')).hexdigest()[2:]
		tid =hashlib.md5((id+str(sig_shift)).encode('utf-8')).hexdigest()[2:]
		id2 = lib.hex2bin(id)
		tid2= lib.hex2bin(tid)
		if str(id2)[:signature_length] == str(tid2)[:signature_length]:
			break
		else:
			sig_shift+=1
	endtime = int(time.time()*1000000)
	postFileText = b64String( name) + "\n"+b64String( subject) + "\n"+b64String( text   ) + "\n"+imageBase64+"\n"+str(curtime)+"\n"+str(sig_shift)+"\n"+b64String(	tags) + "\n"+b64String(	languages)+"\n"+refersto+"\n"+connectedto
	#writing to file
	fd = open("posts/"+str(id),'w')
	fd.write(postFileText)
	fd.close()
	# adding connectedto links
	refersto_list = refersto.split(",")
	for postid in refersto_list:
		lib.addPostConnectedTo(postid,id)

	print("Post with id "+id+" created. [singature length: "+str(lib.getPostSignatureLength(id))+", time = "+str((endtime-starttime)/1000000)+"s, "+str(sig_shift*2)+" hashes] ")
"""
name = raw_input("Name: ")
subject = raw_input("Subject: ")
text = raw_input("Text: ")
imagePath = raw_input("Image name (put file in /img folder first): ")
tags = raw_input("Tags (comma separated): ")
languages = "ru,en"
refersto = raw_input("Insert links to other posts to make an answer (comma separated): ")
np = lib.NewPost(name,subject,text,imagePath,tags,refersto,"en,ru",5)