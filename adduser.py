#!/usr/bin/env python
import os
from config import *
from lib import *
import protocol_pb2
from hashlib import md5
checkDirs()
admins = protocol_pb2.BoardAdministration()
admins.ParseFromString(readFile(administrationFile))
for admin in admins.list:
	log( "["+admin.name+"]")
	log("		can delete posts	:"+str(admin.deleting))
	log("		can sign as mod		:"+str(admin.modsigning))
	log("		modsign 		:"+str(admin.modsign))
name = raw_input("Enter new user name or enter existing user name to delete it: ")

flag = True
for i in admins.list:
	if i.name == name:
		admins.list.remove(i)
		flag = False
if name == "":
	flag = False
if flag:
	password = md5source(raw_input("Enter new user password: "))
	deleting = bool(raw_input("Allow this user to delete posts? [0-No, 1-Yes]: "))
	modsigning = bool(raw_input("Allow this user to sign posts as mod? [0-No, 1-Yes]: "))
	if modsigning:
		modsign = raw_input("Enter modsign for this user (RAW HTML): ")


	entry = admins.list.add()
	entry.name = name
	entry.passwordmd5= password
	entry.deleting = deleting
	entry.modsigning = modsigning
	if modsigning:
		entry.modsign = modsign
	log("[added: "+str(entry.name)+"]")
else:
	if name != "":
		log( "Deleted: "+name)
writeFile(administrationFile,admins.SerializeToString())