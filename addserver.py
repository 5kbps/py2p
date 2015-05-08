#!/usr/bin/env python
import os
from config import *
from lib import *
import protocol_pb2

checkDirs()
servers = protocol_pb2.ServersList()
servers.ParseFromString(readFile(serversListFile))
for server in servers.list:
	print "[",server.address,"]"
	print "		rejected connections    :",str(server.rejected)
	print "		received posts		:",str(server.received)
	print "		new 			:",str(server.new)
hostname = raw_input("Enter server address:")
host = hostname.split(":")[0]
if len(hostname.split(":"))==1:
	port = 5441
else:
	port = toInt(hostname.split(":")[1],5441)
if valid.hostname(host):
	entry = servers.list.add()
	entry.address = host+":"+str(port)
	entry.rejected = 0
	entry.received  = 0
	entry.new = True
	print "[added: ",entry.address,"]"
else:
	print "[not a host!]"
writeFile(serversListFile,servers.SerializeToString())