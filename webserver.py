#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import os
import cgi
import protocol_pb2
from lib import *
from config import *
from xml.sax.saxutils import escape, unescape
import config
import time

mimetypes = {
	"html": "text/html",
	"css": "text/css",
	"js": "application/javascript",
	"jpg": "image/jpg",
	"jpeg": "image/jpg",
	"png": 	"image/png",
	"svg": "image/svg+xml",
	"gif": "image/gif"
}
supported_image_formats = ['jpg','gif','png','jpeg']
def unescapeHTML(text):
	html_escape_table = {
		'"': "&quot;",
		"'": "&apos;"
	}
	html_unescape_table = {v:k for k, v in html_escape_table.items()}
	return unescape(text, html_unescape_table)

#posts
def sortPostsByDate(postlist):
	post_d = {}
	for post in postlist:
		if post in get['time']:
			post_d[post] = get['time'][post]
	sorted_d = sorted(post_d, key=post_d.__getitem__,reverse=True)
	return sorted_d
def cutLatestPosts(postlist,number,shift=0):
	post_d = sortPostsByDate(postlist)
	return list(postlist)[shift:number+shift]
class ThumbCreatorClass():
	def __init__(self):
		to = "do"
	def genThumbs(self):
		print ":genThumbs"
		for post in get['received']:
			self.genPostThumbs(readPost(post))
	def genPostThumbs(self,post):
		if not hasattr(post,"id"):
			post = readPost(post)
		size = webServerThumbnailSize
		for img_file in post.files:
			if hasattr(img_file,"name") and hasattr(img_file,"source") and hasattr(img_file,"md5hash"):
				filename = postsFileDir+img_file.md5hash+"."+getExt(img_file.name)
				if not fileExists(webserverImageThumbDir+img_file.md5hash+".jpg"):
					try:
						im = Image.open(filename).convert('RGB')
						im.thumbnail(size)
						im.save(webserverImageThumbDir+img_file.md5hash+".jpg", "JPEG",quality=webServerThumbnailQuality)
					except IOError as e:
						print "cannot create thumbnail for", postid, e
			else:
				print "		cannot create thumbnail"
class PageViewerClass():
	def __init__(self):
		to = "do"
		self.errorsHTML = {
			"post_404": "<h1>404</h1><br><hr> Post not found"
		}

#k	def cacheHTML(self,page,html):
	def rawPostHTML(self,postid):
		if fileExists(webserverPostsDir+postid) and postid in get['received']:
			return readFile(webserverPostsDir+postid)
		else:
			return HTMLGenerator.genPostHTML(postid)
	def showPost(self,postid):
		if fileExists(webserverPostsDir+postid):
			header_replacements = {
				"title": "Post "+postid+" - py2p",
				"head": "<script src=\"/static/postView.js\"></script>" 
			}
			footer_replacements = {
				"took": "{TODO}"
			}
			output = HTMLGenerator.fromTemplate("header",header_replacements)
			output+= self.rawPostHTML(postid)
			output+= HTMLGenerator.fromTemplate("footer",footer_replacements)
			return output
		else:
			return self.errorsHTML["post_404"]
	def rawThreadHTML(self,postid):
		if postid in get['connected']:
			#output += str(get['connected'][postid])
			output = ""
			for reply in get['connected'][postid]:
				output += self.rawPostHTML(reply)
		else:
			output = "post missed"+postid
		return output

	def showThread(self,postid,shift=0):
		global get			
		shift = shift*webserverPostsOnPage
		header_replacements = {
				"title": "Thread "+postid+" - py2p",
				"head": "<script src=\"/static/threadView.js\"></script>" 
			}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		output+= self.rawPostHTML(postid)
		output += "<hr>"
		postlist = []
		if postid in get['connected']:
			for reply in get['connected'][postid]:
				postlist.append(reply)
		all_length = len(postlist)
		postlist = cutLatestPosts(postlist,webserverPostsOnPage,shift)
		output += "<div class=\"thread_replies\">"
		output += self.rawThreadHTML(postid)
		output += "</div>"
		output += HTMLGenerator.getPageListHTML(all_length,webserverPostsOnPage,shift,"thread/"+postid)
		output += HTMLGenerator.fromTemplate("form")
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
	def showThreads(self):
		global get
		header_replacements = {
			"title":"Threads list",
			"head":""
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		op_list = []
		for op_post in get['connected'].keys():
			op_list.append(op_post)
		for op_post in op_list:
			output += self.rawPostHTML(op_post)
		output+= HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
	def showAll(self,shift=0):
		global get
		shift=shift*webserverPostsOnPage
		postlist = cutLatestPosts( sortPostsByDate(get['received']),webserverPostsOnPage,shift )
		header_replacements = {
			"title":"Latest posts",
			"head":""
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		for post in postlist:
			output += self.rawPostHTML(post)
		output += HTMLGenerator.getPageListHTML(len(get['received']),webserverPostsOnPage,shift,"all")
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
class HTMLGeneratorClass():
	def updateAll(self,postid):
		global get
		self.updatePostHTML(postid)
		ThumbCreator.genPostThumbs(postid)
		if postid in get['refer']:
			self.updatePostHTML(get['refer'][postid])
	def fromTemplate(self,template,replacements={}):
		template = readFile(webserverDir+"templates/"+ template+".tpl","r")
		for replacement in replacements:
			try:
				template = template.replace("%%"+replacement+"%%",replacements[replacement])
			except BaseException as e:
				print "		:fromTemplate:",e
		return template
	def updatePostHTML(self,postid):
		writeFile(webserverPostsDir+postid,self.genPostHTML(postid),"w")
		print "HTML UPDATED",postid
	def makePosts(self):
		for post_file in get['received']:
			writeFile(webserverPostsDir+post_file,self.genPostHTML(post_file),"w")
	def genPostHTML(self,post_file):
		if post_file in get['received']:
			post = readPost(post_file)
			replacements = {
				"name": unescapeHTML( post.name),
				"subject": unescapeHTML( post.subject),
				"text": unescapeHTML(post.text),
				"id": unescape(post.id),
				"filelist": self.getFileListHTML(post),
				"taglist": self.getTagListHTML(post),
				"langlist": self.getLanguagesListHTML(post),
				"replycount":self.getReplyCount(post),
				"pow":self.getPOWValue(post)
			}
			return self.fromTemplate("post",replacements)
		else:
			print "missed:"+ post_file
			return ""# 
	def getFileListHTML(self,post):
		r = "<div class=\"filelist\">\n"
		for post_file in post.files:
			r += "		<span class=\"file\">\n"
			if hasattr(post_file,"name"):
				r+="			<a class=\"filelink\" target=\"_blank\" href=\"/file/"+post_file.md5hash+"."+getExt(post_file.name)+"\">"
				r+="<span class=\"filename\">"
				r+=post_file.name
				r+="</span>\n"
				r+="</a><br>"
				if hasattr(post_file,"md5hash") and getExt(post_file.name) in supported_image_formats:
					r+="			<img class=\"thumb\" src=\"/thumb/"+post_file.md5hash+".jpg\">\n"
			r+= "		</span>\n"
		r+= "	</div>"
		return r
	def getTagListHTML(self,post):
		output = "<span class=\"taglist\">"
		for tag in post.tags:
			output+="<a class=\"tag\" href=\"/tag/"+tag+"\">#"+tag+"</a>"
		output += "</span>"
		return output
	def getLanguagesListHTML(self,post):
		output = "<span class=\"languagelist\">"
		for language in post.languages:
			output+="<img class=\"language\" src=\"/static/flags/"+language+".png\" title=\""+language+"\">"
		output += "</span>"
		return output
	def getReplyCount(self,post):
		global get
		if post.id in get['connected']:
			r = len(get['connected'][post.id])
		else:
			return ""
		output = "<span class=\"replycounter "
		if r >= 1000:
			output += "m1000\"><a class=\"small_reply_counter\" href=\"/thread/"+post.id+"\">Replies: <span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		if r >= 500:
			output += "m500\"><a class=\"small_reply_counter\" href=\"/thread/"+post.id+"\">Replies: <span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		if r >= 100:
			output += "m100\"><a class=\"small_reply_counter\" href=\"/thread/"+post.id+"\">Replies: <span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		if r >= 50:
			output += "m50\"><a class=\"small_reply_counter\" href=\"/thread/"+post.id+"\">Replies: <span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		if r >= 10:
			output += "m10\"><a class=\"small_reply_counter\" href=\"/thread/"+post.id+"\">Replies: <span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		if r >= 5:
			output += "m5\"><a class=\"small_reply_counter\" href=\"/thread/"+post.id+"\">Replies: <span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		if r >= 1:
			output += "m1\"><a class=\"small_reply_counter\" href=\"/thread/"+post.id+"\">Replies: <span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		else:
			return ""
	def getPOWValue(self,post):
		global get
		if post.id in get['pow']:
			r = get['pow'][post.id]
		else:
			return ""
		output = "<span class=\"powcounter "
		if r >= 40:
			output += "pow_40\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">POW: <span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 35:
			output += "pow_35\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">POW: <span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 30:
			output += "pow_30\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">POW: <span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 25:
			output += "pow_25\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">POW: <span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 20:
			output += "pow_20\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">POW: <span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		else:
			output += "pow_0\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">POW: <span class=\"pow\">"+str(r)+"</span></a></span>"
			return output

	def getPageListHTML(self,listlength,pagesize,shift,prefix):
		cur_page_num = shift/pagesize
		page_count = listlength/pagesize
		output = "<div class=\"pagelist\">"
		if cur_page_num != 0:
			output += "<span class=\"firstpage\"><a class=\"pagelink\" href=\"/"+str(prefix)+"/"+str(cur_page_num-1)+"\">[<-]</a></span>"
		for page_num in range(0,page_count+1):
			if page_num == cur_page_num:
				output += "<span class=\"currentpage\">["+str(page_num)+"]</span>"
			else:
				output += "<span class=\"pageitem\"><a class=\"pagelink\" href=\"/"+str(prefix)+"/"+str(page_num)+"\">["+str(page_num)+"]</a></span>"
		if cur_page_num < page_count:
			output += "<span class=\"lastpage\"><a class=\"pagelink\" href=\"/"+str(prefix)+"/"+str(cur_page_num+1)+"\">[->]</a></span>"
		output += "</div>"
		return output

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
	def send_static(self,path = 0):
		if path == 0:
			path = self.path
			filepath = webserverDir+path
		else:
			path = self.path
			filepath = path
			filepath = filepath.replace('/file/','file/')
		mimetype = mimetypes[path.split('.')[len(path.split('.'))-1]]
		if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
			f = open(filepath,'r') 
			self.send_response(200)
			self.send_header('Content-type',mimetype)
			self.end_headers()
			self.wfile.write(f.read())
			f.close()
		else:
			self.send_response(404)
			self.send_header('Content-type',"text/html")
			self.end_headers()
			self.wfile.write("404 Not found")
		return True
	def send(self,output):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write(output)

	def do_GET(self):
		updateDB(HTMLGenerator.updateAll)
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
		starttime = time.time()
		path_list = removeEmptyItems( self.path.split("/"))
		path_length = len(path_list)
		if self.path.split(".")[len(self.path.split("."))-1] in mimetypes.keys():
			if path_list[1]=="file":
				self.send_static(path_list[2])
			else:
				self.send_static()
		if path_length == 0:
			output = PageViewer.showAll()		
		if path_length == 1:
			if path_list[0]=="threads":
				output = PageViewer.showThreads()
			if path_list[0]=="all":
				output = PageViewer.showAll()
		if path_length == 2:
			if path_list[0]=="rawpost":
				output = PageViewer.rawPostHTML(path_list[1])
			if path_list[0]=="post" :
				output = PageViewer.showPost(path_list[1])
				self.send(output)
			if path_list[0]=="rawthread" :
				output = PageViewer.rawThreadHTML(path_list[1])
				self.send(output)
			if path_list[0]=="thread" :
				if len(path_list) > 2:
					shift = toInt(path_list[2])
				else:
					shift = 0
				output = PageViewer.showThread(path_list[1],shift)		
			if path_list[0]=="file" :
				self.send_static(self.path)
			if path_list[0]=="all" and toInt(path_list[1],0)>=0:
				output = PageViewer.showAll(toInt(path_list[1]))

		if output != "":
			self.send(output)
		print time.time()-starttime
	def getParamFromForm(self,form,param):
		if param in form and hasattr(form[param],"value"):
			return form[param].value
		else:
			return ""
	def getFileFromForm(self,form,param):
		if param in form and hasattr(form[param],"file"):
			return form[param].file.read()
		else:
			return "",""

	def do_POST(self):
		if self.path=="/send":
			# creating new post
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})

			proceed = True
			name = self.getParamFromForm(form,"name")
			subject = self.getParamFromForm(form,"subject")
			text = self.getParamFromForm(form,"text")
			imageName = self.getParamFromForm(form,"image")
			files = {}
			i = 1
			'''
			while self.getFileFromForm(form,"file"+str(i)) != "":
				files[str(i)] = {
					"name": self.getParamFromForm(form,"file"+str(i)),
					"source": self.getFileFromForm(form,"file"+str(i))
				}
				i+=1
			'''
			refer = self.getParamFromForm(form,"refer")

			tags = "tag,test,webposting"
			languages = "ru,en"
			#id = lib.NewPostFromWS(name,subject,text,imageExt,imageB64,tags,refersto,languages)
			#host = self.getHeader("Host")
			self.send_response(200)	
			self.send_header('Content-type','text/html')
#				self.send_header('Location',"http://"+host+'/post/'+id)
			self.end_headers()
			self.wfile.write(text+";")



global get
initDB()
HTMLGenerator = HTMLGeneratorClass()
HTMLGenerator.makePosts()
PageViewer = PageViewerClass()
ThumbCreator = ThumbCreatorClass()
ThumbCreator.genThumbs()
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