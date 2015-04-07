#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from hashlib import md5
from base64 import b64encode
import urllib
import time
import socket
from lib import datop
from lib import *

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

def CreatePost(name="",subject="",text="",imagePath="",tags="default,tag",refersto=0,languages="en,ru",signature_length=1):
	imageExt= imagePath[-3:]
	imageHash = datop.getFileHash("img/"+imagePath)
	curtime = int(time.time()*10000)
	tags = datop.trimStringAsList(tags)
	languages = datop.trimStringAsList(languages)
	connectedto =""
	sig_shift = 0
	print "Generating \"proof of work\" signature. It can take some time (approximately "+str(lib.getApproxTimeBySignatureLength(signature_length))+"s)"
	starttime = int(time.time()*1000000)
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
	postFileText = b64String( name) + "\n"+b64String( subject) + "\n"+b64String( text   ) + "\n"+imageBase64+"\n"+str(curtime)+"\n"+str(sig_shift)+"\n"+b64String(	tags) + "\n"+b64String(	languages)+"\n"+refersto+"\n"+connectedto
	#writing to file
	fd = open("posts/"+str(datop.int36(int(id,16))),'w')
	fd.write(postFileText)
	fd.close()
	# adding connectedto links
	refersto_list = refersto.split(",")
	for postid in refersto_list:
		lib.addPostConnectedTo(postid,id)

	print("Post with id "+id+" created. [singature length: "+str(lib.getPostSignatureLength(id))+", time = "+str((endtime-starttime)/1000000)+"s, "+str(sig_shift*2)+" hashes] ")

name = raw_input("Name: ")
subject = raw_input("Subject: ")
text = raw_input("Text: ")
imagePath = raw_input("Image name (put file in /img folder first): ")
tags = raw_input("Tags (comma separated): ")
languages = "ru,en"
refersto = raw_input("Insert links to other posts to make an answer (comma separated): ")
np = CreatePost(name,subject,text,imagePath,tags,refersto,"en,ru",5)
