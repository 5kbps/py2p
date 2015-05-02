#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import os
import cgi
import protocol_pb2
from lib import *
from xml.sax.saxutils import escape, unescape
import config
import time

initDB()
def unescapeHTML(text):
	html_escape_table = {
		'"': "&quot;",
		"'": "&apos;"
	}
	html_unescape_table = {v:k for k, v in html_escape_table.items()}
	return unescape(text, html_unescape_table)

class HTMLGenerator():
	def makePosts(self):
		for post_file in get['received']:
			writeFile(webserverDir+"posts/"+post_file,self.genPostHTML(post_file),"w")
	def genPostHTML(self,post):
		for post_file in get['received']:
			post = readPost(post_file)
			replacements = {
				"name": unescapeHTML( post.name),
				"subject": unescapeHTML( post.subject),
				"text": unescapeHTML(post.text)
			}
			return self.fromTemplate("post",replacements)
	def fromTemplate(self,template,replacements):
		template = readFile(webserverDir+"templates/"+ template+".tpl","r")
		for replacement in replacements:
			template = template.replace("%%"+replacement+"%%",replacements[replacement])
		return template
HTMLGenerator().makePosts()
class myHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		starttime = int(time.time()*1000000)
		message_parts = [
			'CLIENT VALUES:',
			'client_address=%s (%s)' % (self.client_address,
										self.address_string()),
			'command=%s' % self.command,
			'path=%s' % self.path,
			'request_version=%s' % self.request_version,
			'',
			'SERVER VALUES:',
			'server_version=%s' % self.server_version,
			'sys_version=%s' % self.sys_version,
			'protocol_version=%s' % self.protocol_version
		]
		output = ""
		if self.path.split(".")[len(self.path.split("."))-1] in ["css","js","jpg","png","gif","svg"]:
			self.send_static()
			#Open the static file requested and send it
	#Handler for the GET requests
	def send_static(self):
		passRequest = False
		if self.path.endswith(".js"):
			passRequest = True
			mimetype='application/javascript'
		if self.path.endswith(".css"):
			passRequest = True
			mimetype='text/css'
		if self.path.endswith(".jpg"):
			passRequest = True
			mimetype='image/jpg'
		if self.path.endswith(".jpeg"):
			passRequest = True
			mimetype='image/jpg'
		if self.path.endswith(".png"):
			passRequest = True
			mimetype='image/png'
		if self.path.endswith(".svg"):
			passRequest = True
			mimetype='image/svg+xml'
		if self.path.endswith(".gif"):
			passRequest = True
			mimetype='image/gif'
		if passRequest == True:
			filepath = webserverDir+self.path
			if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
				f = open(filepath,'r') 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			else:
				self.send_response(404)
				self.end_headers()
				self.wfile.write("404 not found")
			return True
		else:
			return False

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', webServerPort), myHandler)
	print 'Started httpserver on port ' , webServerPort
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()