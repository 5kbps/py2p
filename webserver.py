#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import os, cgi, setproctitle
import protocol_pb2
from lib import *
import re
from config import *
import bbcode
from xml.sax.saxutils import escape, unescape
import time, datetime
checkDirs()
setproctitle.setproctitle("py2pserver")
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
def unescapeHTML(text):
	html_escape_table = {
		'"': "&quot;",
		"'": "&apos;"
	}
	html_unescape_table = {v:k for k, v in html_escape_table.items()}
	return unescape(text, html_unescape_table)
def escapeHTML(text):
	html_escape_table = {
	    '"': "&quot;",
	    "'": "&apos;",
	    "\n":"<br>"
	}
	return escape(text, html_escape_table)

#posts
def sortPostsByDate(postlist,newOnTop = True):
	post_d = {}
	for post in list(postlist):
		if post in get['timestamp']:
			post_d[post] = get['timestamp'][post]
	sorted_d = sorted(post_d, key=post_d.__getitem__,reverse=newOnTop)
	return sorted_d
def cutLatestPosts(postlist,number,shift=0):
	post_d = sortPostsByDate(postlist)
	return list(postlist)[shift:number+shift]

#thumbs
class ThumbCreatorClass():
	def __init__(self):
		pass
	def genThumbs(self):
		print ":genThumbs"
		for post in get['received']:
			self.genPostThumbs(readPost(post))
	def genPostThumbs(self,post):
		if not hasattr(post,"id"):
			post = readPost(post)
		size = webServerThumbnailSize
		for img_file in post.files:
			if hasattr(img_file,"name") and hasattr(img_file,"source") and hasattr(img_file,"md5hash") and getExt(img_file.name) in webServerSupportedImageFormats:
				filename = postsFileDir+img_file.md5hash+"."+getExt(img_file.name)
				if not fileExists(webServerImageThumbDir+img_file.md5hash+".jpg"):
					try:
						im = Image.open(filename).convert('RGB')
						im.thumbnail(size)
						im.save(webServerImageThumbDir+img_file.md5hash+".jpg", "JPEG",quality=webServerThumbnailQuality)
					except IOError as e:
						print "cannot create thumbnail for", post.id, e
			else:
				print "		cannot create thumbnail"
class PageViewerClass():
	def __init__(self):
		to = "do"
		self.errorsHTML = {
			"post_404": "<h1>404</h1><br><hr> Post not found"
		}
	def rawPostHTML(self,postid):
		if fileExists(webServerPostsDir+postid) and postid in get['received']:
			return readFile(webServerPostsDir+postid)
		else:
			HTMLGenerator.updatePostHTML(postid)
			return readFile(webServerPostsDir+postid) 
	def showPost(self,postid):
		if fileExists(webServerPostsDir+postid):
			header_replacements = {
				"title": "Post "+postid+" - py2p",
				"head": "<script src=\"/static/postView.js\"></script>" 
			}
			form_replacements = {
				"replyto": postid
			}
			footer_replacements = {
				"took": "{TODO}"
			}
			output = HTMLGenerator.fromTemplate("header",header_replacements)
			output+= self.rawPostHTML(postid)
			output+= HTMLGenerator.fromTemplate("form",form_replacements)
			output+= HTMLGenerator.fromTemplate("footer",footer_replacements)
			return output
		else:
			return self.errorsHTML["post_404"]
	def showTree(self,postid):
		global get
		header_replacements = {
				"title": "Tree view "+postid+" - py2p",
				"head": "<script src=\"/static/threadView.js\"></script>" 
		}
		form_replacements = {
			"replyto": postid
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		output += self.rawTreeHTML(postid)
		output += HTMLGenerator.fromTemplate("form",form_replacements)
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
	def rawTreeHTML(self,postid,reqLevel=0,cutOn=webServerTreeViewCutOn):
		if postid in get['received']:
			output = self.rawPostHTML(postid)
			if reqLevel < webServerTreeViewRecursionLevel:
				if postid in get['connected']:
					sortedList = []	
					for reply in get['connected'][postid]:
						sortedList.append(reply)
					sortedList = sortPostsByDate(sortedList,False)
					output += "<div class=\"thread_replies\">"
					threadhtml = ""
					if len(sortedList) > cutOn:
						delta = len(sortedList) - cutOn
						sortedList = sortedList[:cutOn]
						for reply1 in sortedList:
							threadhtml += self.rawTreeHTML(reply1,reqLevel+1,cutOn)
						output += "<div class=\"cutoff\"><a class=\"cutofflink\" href=\"/thread/"+postid+"\">Posts hidden: "+str(len(list(get['connected'][postid])) -cutOn)+"</a></div>"
						output += threadhtml
					else:
						for reply1 in sortedList:
							output += self.rawTreeHTML(reply1,reqLevel+1,cutOn)
					output += "</div>"
			else:
				if postid in get['connected']:
					output += "<div class=\"cutoff\"><a class=\"cutofflink\" href=\"/tree/"+postid+"\">Show deeper: "+str(len(list(get['connected'][postid])))+"</a></div>"
			return output
		else:
			return "POST NOT FOUND"
	def showTrees(self,shift=0):
		global get

		shift = shift*webServerPostsOnPage

		header_replacements = {
			"title":"Trees list",
			"head":""
		}
		form_replacements = {
			"replyto": "nobody"
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		postlist = []
		for postid in get['connected'].keys():
			if HTMLGenerator.isTree(postid):
				postlist.append(postid)
		all_length = len(postlist)
		postlist = cutLatestPosts( sortPostsByDate(postlist),webServerPostsOnPage,shift )
		for postid in postlist:
			output += self.rawPostHTML(postid)
		output += HTMLGenerator.getPageListHTML(all_length,webServerPostsOnPage,shift,"trees/")
		output+= HTMLGenerator.fromTemplate("form",form_replacements)
		output+= HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
	def rawThreadHTML(self,postid):
		if postid in get['connected']:
			#output += str(get['connected'][postid])
			output = ""
			sortedList= sortPostsByDate(get['connected'][postid],False)
			for reply in sortedList:
				output += self.rawPostHTML(reply)
		else:
			output = ""
		return output
	def showThread(self,postid,shift=0):
		global get			
		shift = shift*webServerPostsOnPage
		header_replacements = {
				"title": "Thread "+postid+" - py2p",
				"head": "<script src=\"/static/threadView.js\"></script>" 
			}
		footer_replacements = {
			"took": "{TODO}"
		}
		form_replacements = {
			"replyto": postid
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		output+= self.rawPostHTML(postid)
		postlist = []
		if postid in get['connected']:
			for reply in get['connected'][postid]:
				postlist.append(reply)
		all_length = len(postlist)
		postlist = cutLatestPosts(postlist,webServerPostsOnPage,shift)
		output += "<div class=\"thread_replies\">"
		output += self.rawThreadHTML(postid)
		output += "</div>"
		output += HTMLGenerator.getPageListHTML(all_length,webServerPostsOnPage,shift,"thread/"+postid)
		output += HTMLGenerator.fromTemplate("form",form_replacements)
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
	def showThreads(self):
		global get
		header_replacements = {
			"title":"Threads list",
			"head":""
		}
		form_replacements = {
			"replyto": "nobody"
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
		output+= HTMLGenerator.fromTemplate("form",form_replacements)
		output+= HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
	def showAll(self,shift=0):
		global get
		shift=shift*webServerPostsOnPage
		postlist = cutLatestPosts( sortPostsByDate(get['received']),webServerPostsOnPage,shift )
		header_replacements = {
			"title":"Latest posts",
			"head":""
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		form_replacements = {
			"replyto": "nobody"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		for post in postlist:
			output += self.rawPostHTML(post)
		output += HTMLGenerator.getPageListHTML(len(get['received']),webServerPostsOnPage,shift,"all")
		output += HTMLGenerator.fromTemplate("form",form_replacements)
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output

	def showTag(self,tag,shift=0):
		global get
		shift=shift*webServerPostsOnPage
		if tag in get['bytag']:
			postlist = cutLatestPosts( sortPostsByDate(get['bytag'][tag]),webServerPostsOnPage,shift )
		else:
			postlist = []

		header_replacements = {
			"title":"Tag search: #"+tag,
			"head":""
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		form_replacements = {
			"replyto": "nobody"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		for post in postlist:
			output += self.rawPostHTML(post)
		output += HTMLGenerator.getPageListHTML(len(get['received']),webServerPostsOnPage,shift,"tag/"+tag)
		output += HTMLGenerator.fromTemplate("form",form_replacements)
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output


class HTMLGeneratorClass():
	def fromTemplate(self,templateName,replacements={}):
		template = readFile(webServerTemplatestDir+templateName+".tpl","r")
		for replacement in replacements:
			try:
				template = template.replace("%%"+replacement+"%%",replacements[replacement])
			except BaseException as e:
				print "		:fromTemplate:",e
		return template
	def updatePostHTML(self,postid):
		writeFile(webServerPostsDir+postid,self.genPostHTML(postid),"w")
		if postid in get['refer']:
			self.updatePostHTML(get['refer'][postid])
		print ":updatePostHTML updated ",postid
	def makePosts(self):
		for post_file in get['received']:
		#	if not fileExists(webServerPostsDir+post_file):
			writeFile(webServerPostsDir+post_file,self.genPostHTML(post_file),"w")
	def genPostHTML(self,post_file):
		if post_file in get['received']:
			post = readPost(post_file)
			replacements = {
				"name": escapeHTML( post.name),
				"subject": escapeHTML( post.subject),
				"text": BBCodeParser.format(post.text),
				"id": escapeHTML(post.id),
				"filelist":  self.getFileListHTML(post),
				"taglist":  self.getTagListHTML(post),
				"langlist":  self.getLanguagesListHTML(post),
				"replycount":self.getReplyCount(post),
				"pow":self.getPOWValue(post),
				"time":self.getHumanReadableTime(post.id),
				"treelink":self.treeLink(post.id),
				"uplink":self.upLink(post.id),
				"modsign":self.getModSignHTML(post.id)
			}
			return self.fromTemplate("post",replacements)
		else:
			print "missed:"+ post_file
			return ""
	def newPostHTML(self,post):
		header_replacements = {
			"title":"Post created!",
			"head":""
		}
		newpost_replacements = {
			"id":  post.id
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		output += HTMLGenerator.fromTemplate("newpost",newpost_replacements)
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output
	def getHumanReadableTime(self,postid):
		global get
		if postid in get['timestamp']:
			timestamp = float(get['timestamp'][postid])/10000
			timestamp = datetime.datetime.fromtimestamp(timestamp)
			timestr = timestamp.strftime('<span class=\"date\">%d.%m.%Y </span><span class=\"time\">%H:%M:%S</span>')
		else:
			timestr = "UNKNOWN TIME"
		return timestr
	def getModSignHTML(self,postid):
		global get
		if postid in get['protected'] and "html" in get['protected'][postid]:
			return get['protected'][postid]['html']
		else:
			return ""
	def getFileListHTML(self,post):
		r = "<div class=\"filelist\">\n"
		for post_file in post.files:
			r += "		<span class=\"file\">\n"
			if hasattr(post_file,"name"):
				r+="			<a class=\"filelink\" target=\"_blank\" href=\"/file/"+post_file.md5hash+"."+escapeHTML( getExt(post_file.name))+"\">"
				r+="<span class=\"filename\">"
				r+= escapeHTML( post_file.name )
				r+="</span>\n"
				r+="</a><br>"
				if hasattr(post_file,"md5hash") and getExt(post_file.name) in webServerSupportedImageFormats:
					r+="			<img class=\"thumb\" src=\"/thumb/"+post_file.md5hash+".jpg\">\n"
			r+= "		</span>\n"
		r+= "	</div>"
		return r
	def getTagListHTML(self,post):
		output = "<span class=\"taglist\">"
		for tag in post.tags:
			output+="<a class=\"tag\" href=\"/tag/"+escapeHTML( tag)+"\">#"+escapeHTML(tag)+"</a>"
		output += "</span>"
		return output
	def getLanguagesListHTML(self,post):
		output = "<span class=\"languagelist\">"
		for language in post.languages:
			output+="<img class=\"language\" src=\"/static/flags/"+escapeHTML( language )+".png\" title=\""+escapeHTML( language)+"\">"
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
	def isTree(self,postid):
		r = False
		if postid in get['connected']:
			for reply in get['connected'][postid]:
				if reply in get['connected']:
					if len(get['connected'][reply])>0:
						r = True
						break
		return r
	def treeLink(self,postid):
		if self.isTree(postid):
			return "<span class=\"posttreelink\"><a class=\"treelink\" href=\"/tree/"+postid+"\">Tree</a></span>"
		else:
			return ""
	def upLink(self,postid):
		if postid in get['refer']:
			if isReceived(get['refer'][postid]):
				return "<span class=\"posttreelink\"><a class=\"treelink\" href=\"/tree/"+get['refer'][postid]+"\">Up</a></span>"
			else:
				return ""
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
		if listlength%pagesize == 0:
			page_count -= 1
		output = "<div class=\"pagelist\">"
		if cur_page_num != 0:
			output += "<span class=\"firstpage\">"
			output += "<a class=\"pagelink\" href=\"/"+str(prefix)+"/"+str(cur_page_num-1)+"\"><</a></span>"
		for page_num in range(0,page_count+1):
			
			if page_num == cur_page_num:
				output += "<span class=\"currentpage\"><span class=\"currentpagenum\">"+str(page_num)+"</span></span>"
			else:
				output += "<span class=\"pageitem\"><a class=\"pagelink\" href=\"/"+str(prefix)+"/"+str(page_num)+"\">"+str(page_num)+"</a></span>"
			if page_num % webServerPageListSplitNum == webServerPageListSplitNum-1:
				output +="</div>"
				output += "<div class=\"pagelist\">"
		if cur_page_num < page_count:
			output += "<span class=\"lastpage\"><a class=\"pagelink\" href=\"/"+str(prefix)+"/"+str(cur_page_num+1)+"\">></a></span>"
		output += "</div>"
		return output

class myHandler(BaseHTTPRequestHandler):
	#Handler for the GET requests
	def send_static(self,path = 0):
		if path == 0:
			path = self.path
			filepath = webServerDir+path
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

		print urllib.unquote(self.path).decode('utf8')
		path_list = removeEmptyItems( urllib.unquote(self.path).decode('utf8').split("/"))
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
			if path_list[0]=="trees":
				output = PageViewer.showTrees()
			if path_list[0]=="all":
				output = PageViewer.showAll()

		if path_length == 2:
			if path_list[0]=="rawpost":
				output = PageViewer.rawPostHTML(path_list[1])
			if path_list[0]=="post":
				output = PageViewer.showPost(path_list[1])
			if path_list[0]=="rawthread" :
				output = PageViewer.rawThreadHTML(path_list[1])
			if path_list[0]=="thread" :
				if len(path_list) > 2:
					shift = toInt(path_list[2])
				else:
					shift = 0
				output = PageViewer.showThread(path_list[1],shift)
			if path_list[0]=="tree":
				output = PageViewer.showTree(path_list[1])		
			if path_list[0]=="file" :
				self.send_static(self.path)
			if path_list[0]=="all":
				output = PageViewer.showAll(toInt(path_list[1],0))
			if path_list[0]=="trees":
				output = PageViewer.showTrees(toInt(path_list[1],0))
			if path_list[0]=="tag":
				output = PageViewer.showTag(path_list[1],0)

		if path_length == 3:
			if path_list[0]=="tag":
				output = PageViewer.showTag(path_list[1],toInt(path_list[2],0))

		if output != "":
			self.send(output)
		print time.time()-starttime
	def getParamFromForm(self,form,param):
		if param in form and hasattr(form[param],"value"):
			return form[param].value
		else:
			return ""

	def do_POST(self):
		if self.path=="/send":
			# creating new post
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
				'CONTENT_TYPE':self.headers['Content-Type'],
			})

			'''
			self.wfile.write('Client: %s\n' % str(self.client_address))
			self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
			self.wfile.write('Path: %s\n' % self.path)
			self.wfile.write('Form data:\n')
			'''
			proceed = True
			errMessage = ''
			if proceed:
				name = self.getParamFromForm(form,"name")
				subject = self.getParamFromForm(form,"subject")
				text = self.getParamFromForm(form,"text")
				refer = self.getParamFromForm(form,"refer")
				files = []
				for i in range(1,webServerPostingMaxFileCount+1):
					filename = self.getParamFromForm(form,"filename_"+str(i))
					filesource = valid.base64URL( self.getParamFromForm(form,"source_"+str(i)))
					filesize = len(filesource)
					if filename and filesource:
						if filesize <= webServerPostingMaxFileSize:
							files.append({
							"name": filename,
							"source":filesource
							})
						else:
							proceed = False
							errMessage += "file "+filename+" is too big ["+str(filesize)+"] limit: "+str(webServerPostingMaxFileSize)+"<br>"
					else:
						proceed = False
						errMessage += "Filename is empty"
				tags = webServerAdditionalTags
				languages = webServerAdditionalLanguages
				self.send_response(200)
				self.send_header('Content-type','text/html')
	#				self.send_header('Location',"http://"+host+'/post/'+id)
				self.end_headers()
				if proceed:
					self.wfile.write(createPost(name,subject,text,refer,files,tags,languages))
				else:
					self.wfile.write(errMessage)
def createPost(name,subject,text,refer,files,tags,languages):
	current_time = int(time.time()*10000)
	post = protocol_pb2.Post()
	post.name = unicode(name.strip())
	post.subject = unicode(subject.strip())
	post.text = unicode(text.strip())
	post.time = str(current_time)
	for fileentry in files:
		fo = post.files.add()
		fo.name = fileentry['name']
		fo.md5hash = md5source( fileentry['source'] )
		fo.source = fileentry['source']
		print fo.md5hash
	tag_list = string2list(unicode(tags))
	languages_list = string2list(unicode(languages))
	for tag in tag_list:
		if valid.tag(tag):
			to = post.tags.append(tag)
	for lang in languages_list:
		if valid.lang(lang):
			lo = post.languages.append(lang)
	if isReceived(refer.strip()): 	
		post.refer = refer.strip()
	post_content = stringifyPost(post)
	pow_shift = 0
	while True:
		postid1 = md5(post_content+str(pow_shift)).hexdigest()[2:]
		postid2 =md5(str(pow_shift)+post_content).hexdigest()[2:]
		tid1 = hex2bin(postid1)
		tid2= hex2bin(postid2)
		if str(tid1)[:webServerPostingPOW] == str(tid2)[:webServerPostingPOW]:
			break
		else:
			pow_shift+=1
	post.pow = pow_shift
	post.id = int36(int(postid1,16))
	postFileText = post.SerializeToString()
	if post.ByteSize() <= maxPostSize:
		fd = open(postsDir+post.id,'wb')
		fd.write(postFileText)
		fd.close()
		add2DB(post.id)
		HTMLGenerator.updatePostHTML(post.id)
		ThumbCreator.genPostThumbs(post)
		return HTMLGenerator.newPostHTML(post)
	else:
		return "Post is too large, max post size = "+maxPostSize

global get
initDB()
BBCodeParser = bbcode.Parser()
BBCodeParser.add_simple_formatter('hr', '<hr>')
BBCodeParser.add_simple_formatter('sub', '<sub>%(value)s</sub>')
BBCodeParser.add_simple_formatter('sup', '<sup>%(value)s</sup>')
BBCodeParser.add_simple_formatter('b', '<b>%(value)s</b>')
BBCodeParser.add_simple_formatter('s', '<s>%(value)s</s>')
BBCodeParser.add_simple_formatter('u', '<span class="underlined">%(value)s</span>')
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