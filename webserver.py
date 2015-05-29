#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
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
	"gif": "image/gif",
	"webm": "video/webm"
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
	def genThumbs(self,list_of=0):
		print ":genThumbs"
		if list_of == 0:
			for post in get['received']:
				self.genPostThumbs(readPost(post))
		else:
			for post in list_of:
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
				print "		Not an image file:",img_file.name
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
			"replyto": ""
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		postlist = []
		for postid in get['connected'].keys():
			if isTree(postid):
				if not postid in get['refer']:
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
			"replyto": ""
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
			"replyto": ""
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


		header_replacements = {
			"title":"Tag search: #"+tag,
			"head":""
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		form_replacements = {
			"replyto": ""
		}
		if tag in get['bytag']:
			postlist = cutLatestPosts( sortPostsByDate(get['bytag'][tag]),webServerPostsOnPage,shift )
			output = HTMLGenerator.fromTemplate("header",header_replacements)
			for post in postlist:
				output += self.rawPostHTML(post)
			output += HTMLGenerator.getPageListHTML(len(get['bytag'][tag]),webServerPostsOnPage,shift,"tag/"+tag)
			output += HTMLGenerator.fromTemplate("form",form_replacements)
			output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		else:
			output = HTMLGenerator.fromTemplate("header",header_replacements)
			output += HTMLGenerator.fromTemplate("error",{ "errortitle":"No posts found by tag #"+escapeHTML(tag),"errortext":" "})
			output += HTMLGenerator.fromTemplate("form",form_replacements)
			output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output


class HTMLGeneratorClass():
	def __init__(self):
		self.additionalTagsHTML = ''
		self.fileSelectListHTML = ''
		for tag in webServerAdditionalTags:
			self.additionalTagsHTML+="<a target=\"_blank\" href=\"/tag/"+unicode(tag.strip())+"\" class=\"additionaltag posttag tag\">#"+unicode(tag.strip())+"</a>"
		for i in range(1,webServerPostingMaxFileCount+1):
			self.fileSelectListHTML +=" 					<input id=\"fileselect_"+str(i)+"\"  autocomplete=\"off\"  type=\"file\" onchange=\"handleSelect(this,event);\"><br>"
	def fromTemplate(self,templateName,replacements={}):
		template = readFile(webServerTemplatestDir+templateName+".tpl","r")
		if templateName == "form":
			replacements['additionaltags'] = HTMLGenerator.additionalTagsHTML
			replacements['maxfiles'] = str(webServerPostingMaxFileCount)
			replacements['fileselectlist'] = self.fileSelectListHTML
			if 'replyto' in replacements:
				if replacements['replyto'] == '':
					replacements['postingmode'] = "New post"
				else:
					replacements['postingmode'] = "Reply to:"
			else:
				replacements['replyto'] = ''
				replacements['postingmode'] = "New post"
		for replacement in replacements:
			try:
				template = template.replace("%%"+replacement+"%%",replacements[replacement])
			except BaseException as e:
				print "		:fromTemplate:",e
		return template
	def updatePostHTML(self,postid,reqLevel = 0):
		if postid in get['received']:
			writeFile(webServerPostsDir+postid,self.genPostHTML(postid),"w")
			if postid in get['refer'] and reqLevel < 3:
				self.updatePostHTML(get['refer'][postid],reqLevel+1)
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
				"filelist": self.getFileListHTML(post),
				"taglist": self.getTagListHTML(post),
				"langlist": self.getLanguagesListHTML(post),
				"replycount":self.getReplyCount(post),
				"pow":self.getPOWValue(post),
				"time":self.getHumanReadableTime(post.id),
				"treelink":self.treeLink(post.id),
				"uplink":self.upLink(post.id),
				"modsign":self.getModSignHTML(post.id),
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
	def postDeleting(self,errors):
		header_replacements = {
			"title":"Manage board",
			"head":""
		}
		footer_replacements = {
			"took": "{TODO}"
		}
		output = HTMLGenerator.fromTemplate("header",header_replacements)
		output = errors
		output += HTMLGenerator.fromTemplate("footer",footer_replacements)
		return output

	def getHumanReadableTime(self,postid):
		global get
		if not postid in get['timestamp']:
			add2DB(postid)
		if postid in get['timestamp']:
			timestamp = float(get['timestamp'][postid])/10000
			try:
				timestamp = datetime.datetime.fromtimestamp(timestamp)
			except BaseException:
				timestamp = datetime.datetime.fromtimestamp(0)
			timestr = timestamp.strftime('<span class=\"date\">%d.%m.%Y </span><span class=\"time\">%H:%M:%S</span>')
		else:
			timestr = "Unknown time"
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
				if len(post_file.name)-len(getExt(post_file.name)) > webServerPostFileNameMaxLength+len(webServerPostLongFileNameSeparator):
					name = escapeHTML( post_file.name[:webServerPostFileNameMaxLength]+ webServerPostLongFileNameSeparator+getExt(post_file.name))
				else:
					name = escapeHTML(post_file.name)
				r+="			<a class=\"filelink\" target=\"_blank\" href=\"/file/"+post_file.md5hash+"."+escapeHTML( getExt(post_file.name))+"\">"
				r+="<span title=\""+escapeHTML(post_file.name)+"\" class=\"filename\">"
				r+= name
				r+="</span>\n"
				r+="</a><br>"
				if hasattr(post_file,"md5hash") and getExt(post_file.name) in webServerSupportedImageFormats:
					r+="			<img class=\"thumb\" onclick=\"thumbExpand(this);\" src=\"/thumb/"+post_file.md5hash+".jpg\">\n"
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
			rh = "m1"
			if r >= 3:
				rh = "m3"
			if r >= 5:
				rh = "m3"
			if r >= 10:
				rh = "m3"
			if r >= 20:
				rh = "m3"
			if r >= 50:
				rh = "m3"
			if r >= 100:
				rh = "m3"
			if r >= 200:
				rh = "m3"
			if r >= 500:
				rh = "m3"
			if r >= 1000:
				rh = "m3"
			output = "<span class=\"replycounter "+rh+"\">"
			output += "<a class=\"small_reply_counter\" onmouseenter=\"showReplies(this);\"  href=\"/thread/"+post.id+"\"><input type=\"hidden\" class=\"post_replies_list\" autocomplete=\"off\" value=\""+self.getRepliesListHTML(post.id)+"\"> <span class=\"replies_s\">Replies: </span><span class=\"rc\">"+str(r)+"</span></a></span>"
			return output
		else:
			return ""
	def getRepliesListHTML(self,postid):
		r = ''
		if postid in get['connected']:
			for connected in get['connected'][postid]:
				r += connected+","
			r=r[:-1]
		return r
	def treeLink(self,postid):
		if isTree(postid):
			return "<span class=\"posttreelink\"><a class=\"treelink\" href=\"/tree/"+postid+"\">Tree</a></span>"
		else:
			return ""
	def upLink(self,postid):
		if postid in get['refer']:
			if isReceived(get['refer'][postid]):
				return "<span class=\"postuplink\"><a class=\"uplink\" href=\"/tree/"+get['refer'][postid]+"\">Up</a></span>"
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
			output += "pow_40\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">★<span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 35:
			output += "pow_35\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">★<span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 30:
			output += "pow_30\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">★<span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 25:
			output += "pow_25\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">★<span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		if r >= 20:
			output += "pow_20\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">★<span class=\"pow\">"+str(r)+"</span></a></span>"
			return output
		else:
			output += "pow_0\"><a class=\"small_pow_counter\" href=\"/thread/"+post.id+"\">★<span class=\"pow\">"+str(r)+"</span></a></span>"
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
		path_list = removeEmptyItems( urllib.unquote(self.path).decode('utf8').split("/"))
		path_length = len(path_list)
		if self.path.split(".")[len(self.path.split("."))-1] in mimetypes.keys():
			if path_list[1]=="file":
				self.send_static(path_list[2])
			else:
				self.send_static()
		else:
			new_posts, removed_posts = updateDB()
			if len(new_posts):
				#generating thumbs for new posts, that are just added 
				ThumbCreator.genThumbs(new_posts)
			for new_post in new_posts:
				HTMLGenerator.updatePostHTML(new_post)

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
		#print time.time()-starttime
	def getParamFromForm(self,form,param):
		if param in form and hasattr(form[param],"value"):
			return form[param].value
		else:
			return ""
	if not webServerloggingEnabled:
		def log_message(self,a1=0,a2=0,a3=0,a4=0,a5=0,a6=0):
			pass

	def do_POST(self):
		# creating new post
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
		})
		path_list = removeEmptyItems( urllib.unquote(self.path).decode('utf8').split("/"))
		path_length = len(path_list)
		if path_list[0]=="manage":
			proceed = True	
			errMessage = ''
			name = self.getParamFromForm(form,"username")
			password = self.getParamFromForm(form,"password")
			to_delete = self.getParamFromForm(form,"manageboard_todelete")
			to_delete = removeEmptyItems( to_delete.split(","))
			if name in get['admins']:
				if md5source( password )==get['admins'][name]['passwordmd5']:
					for item in to_delete:
						if isReceived(item):
							deletePost(item)
							errMessage += "Deleted: "+item+"<br>"
						else:
							errMessage += "Post "+item+" does not exist.<br>"
				else:
					errMessage += "Password or username is not correct<br>"
			else:
				errMessage += "Password or username is not correct<br>"
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(HTMLGenerator.postDeleting(errMessage))
		if path_list[0]=="send":

			'''
			self.wfile.write('Client: %s\n' % str(self.client_address))
			self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
			self.wfile.write('Path: %s\n' % self.path)
			self.wfile.write('Form data:\n')
			'''
			proceed = True
			errMessage = ''
			name = self.getParamFromForm(form,"name")
			subject = self.getParamFromForm(form,"subject")
			text = self.getParamFromForm(form,"text")
			refer = self.getParamFromForm(form,"refer")
			print "R:",refer,len(refer)

			posttime = toInt( self.getParamFromForm(form,"posttime"),0)
			postpowshift = toInt( self.getParamFromForm(form,"postpowshift"),None)
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
					pass
#						proceed = False
#						errMessage += "Filename is empty"
			tags = webServerAdditionalTags+removeEmptyItems( self.getParamFromForm(form,"tags").split("#") )
			languages = webServerAdditionalLanguages
			self.send_response(200)
			self.send_header('Content-type','text/html')
#				self.send_header('Location',"http://"+host+'/post/'+id)
			self.end_headers()
			if proceed:
				self.wfile.write(createPost(name,subject,text,refer,files,tags,languages,posttime,postpowshift))
			else:
				self.wfile.write(errMessage)
def createPost(name,subject,text,refer,files,tags,languages,posttime=0,postpowshift=None):
	current_time = int(time.time()*10000)
	post = protocol_pb2.Post()
	post.name = unicode(name)
	post.subject = unicode(subject)
	post.text = unicode(text)
	if posttime == 0:
		post.time = str(current_time)
	else:
		post.time = str(posttime)
	for fileentry in files:
		fo = post.files.add()
		fo.name = fileentry['name']
		fo.md5hash = md5source( fileentry['source'] )
		fo.source = fileentry['source']
		print fo.md5hash
	languages_list = string2list(unicode(languages))
	for tag in tags:
		if valid.tag(unicode(tag.strip())):
			to = post.tags.append(valid.tag(unicode(tag)))
	for lang in languages_list:
		if valid.lang(lang):
			lo = post.languages.append(lang)
	if isReceived(refer): 	
		post.refer = refer
	post_content = stringifyPost(post)
	if not postpowshift==None:
		pow_shift = int(postpowshift)
#		print "md5 pc = ",md5digest(post_content)
		postid1 = md5digest(post_content+str(pow_shift))
	else:
		pow_shift = 0
		while True:
			postid1 = md5digest(post_content+str(pow_shift))
			postid2 = md5digest(str(pow_shift)+post_content)
			tid1 = hex2bin(postid1)
			tid2 = hex2bin(postid2)
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
		ThumbCreator.genPostThumbs(post.id)
		return HTMLGenerator.newPostHTML(post)
	else:
		return "Post is too large, max post size = "+str(maxPostSize)

global get
initDB()
loadAdministration()
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
cutOutdatedPosts()
try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', webServerPort), myHandler)
	print '[Webserver started succesfully!]'
	print '[Open http://127.0.0.1:'+str(webServerPort)+'/ in your browser to explore the local copy of py2p board]'
	print '[Posts avaliable: '+str(len(get['received']))+']'
	print '[Public servers : '+str(len(get['servers'].list))+']'
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()