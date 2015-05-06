#!/usr/bin/env python
import os
from config import *
from lib import *
import protocol_pb2
for post_file in os.listdir(postsDir):
	os.remove(postsDir+post_file)
for post_file in os.listdir(postsFileDir):
	os.remove(postsFileDir+post_file)
for post_file in os.listdir(webserverPostsDir):
	os.remove(webserverPostsDir+post_file)
for post_file in os.listdir(webserverImageThumbDir):
	os.remove(webserverImageThumbDir+post_file)
if os.path.isfile(serversListFile):
	os.remove(serversListFile)
#if os.path.isfile(defaultServersListFile):
#	os.remove(defaultServersListFile)
checkDirs()
servers = protocol_pb2.ServersList()
entry = servers.list.add()
entry.address = "127.0.0.1:5441"
entry.rejected = 0
entry.received  = 0
entry.new = True
writeFile(serversListFile,servers.SerializeToString())
writeFile(defaultServersListFile,servers.SerializeToString())