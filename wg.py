#!/usr/bin/python

import sys
import io
import re
from http.client import HTTPConnection, HTTPResponse
from html.parser import HTMLParser
import json
import atexit

class Application:
	
	connection = None
	
	def __init__(self):
		ArticlesController.getInstance()
		atexit.register(ArticlesController.getInstance().serialize)
	
	def runWithArgs(self,arg1,arg2):
		sys.argv.extend([arg1,arg2])
		self.run()
	
	def run(self):
		if(len(sys.argv)<3):
			quit(1)
		
		srcArticleName = sys.argv[1].replace(" ","_")
		dstArticleName = sys.argv[2].replace(" ","_")
		srcArticle = ArticlesController.getInstance().addArticle(srcArticleName)
		dstArticle = ArticlesController.getInstance().addArticle(dstArticleName)
		
		i=0
		print("iteration", i+1,"staring")
	#	while(not self.search(srcArticle, i, dstArticle)):
		while(not self.search(srcArticleName,i,dstArticleName)):
			i+=1
			print("iteration", i+1,"staring")
		print(srcArticleName)
		print()
	
	def search(self, src, depth, dst):
		ArticlesController.getInstance().getArticle(src).populateArticle()
		#if(depth == 0):
		#	if( ArticlesController.getInstance().getArticle(src).isLinkedTo(ArticlesController.getInstance().getArticle(dst)) ):
		#		print(dst)
		#		return True
		#	else:
		#		return False
		if( ArticlesController.getInstance().getArticle(src).isLinkedTo(ArticlesController.getInstance().getArticle(dst)) ):
			print(dst)
			return True
			
		for article in ArticlesController.getInstance().getArticle(src).getLinkedArticlesNames():
			if(self.search(article,depth-1,dst) == True):
				print(article)
				return True
		return False
				
	#def search(self, articleSource, depthLeft, targetArticle):
	#	print("Search from",articleSource.getArticleName(),"depth left",depthLeft)
	#	if(depthLeft == 0):
	#		#import pdb; pdb.set_trace()
	#		if(articleSource.isLinkedTo(targetArticle)):
	#			print(targetArticle.getArticleName())
	#			return True
	#		else:
	#			return False
	#	if(articleSource.isLinkedTo(targetArticle)):
	#		print(targetArticle.getArticleName())
	#		return True
	#	for linked in articleSource.getLinkedArticlesNN():
	#		print("Searching in",linked.getArticleName(),"..")
	#		if(self.search(linked,depthLeft-1,targetArticle) == True):
	#			print(linked.getArticleName())
	#			return True

class Article:
	def __init__(self,articleName,articleLinks=list(),download=True):
		self.articleName = articleName
		self.articleLinks = articleLinks
		self.populated = False
		if(download):
			self.populateArticle()
		else:
			self.populated=True
	def populateArticle(self):
		if(self.populated):
			return
		articleText = ArticlesController.getInstance().downloadText(self)
		
		class ArticleParser(HTMLParser):
			def __init__(self, parentArticle):
				super().__init__()
				self.articleLinkPattern = re.compile("/wiki/[A-Za-z0-9:;!@#$%^&*()_+=.,/ -]*")
				self.parentArticle = parentArticle
			def handle_starttag(self, tag, attrs):
				if(tag == "a"):
					for attr in attrs:
						if(attr[0] == "href"):
							if(self.articleLinkPattern.match(attr[1])):
								cleanLink = self.clearLink(attr[1])
								#ar = ArticlesRegistry.getInstance()
								#self.parentArticle.addLinkedArticle(ar.getArticle( cleanLink ))
								if(self.checkLink(cleanLink)):
									self.parentArticle.addLinkTo(cleanLink)
			def clearLink(self,link):
				linkCleaner = re.compile("/wiki/([A-Za-z0-9:;!@$%^&*()_+=.,/ -]*)[A-Za-z0-9:;!@#$%^&*()_+=.,/ -]*")
				#print("cleanLink: ", link, " —> ", linkCleaner.findall(link)[0])
				return linkCleaner.findall(link)[0]
			def checkLink(self,link):
				if(link == "Special:Random"):
					return False
				specialRE = re.compile("Special:[A-Za-z0-9;!@#$%^&*()_+=.,/ -]*")
				fileRE = re.compile("File:[A-Za-z0-9;!@#$%^&*()_+=.,/ -]*")
				wikimediaRE = re.compile("Wikimedia:[A-Za-z0-9;!@#$%^&*()_+=.,/ -]*")
				if(specialRE.match(link) or fileRE.match(link) or wikimediaRE.match(link)):
					return False
				return not link == self.parentArticle.getArticleName()
		
		articleParser = ArticleParser(self)
		articleParser.feed(articleText.decode("utf-8"))
		self.populated = True

	def getArticleName(self):
		return self.articleName
	def getLinkedArticlesNames(self):
		return self.articleLinks
	def getLinkedArticles(self):
		ret = list()
		for articleName in self.articleLinks:
			ret.append(ArticlesController.getInstance().getArticle(articleName,[self]))
		return ret
	def isLinkedTo(self,otherArticle):
		for linkedArticleName in self.articleLinks:
			#if(otherArticle.getArticleName() == "Air_quality"):
			if(linkedArticleName == otherArticle.getArticleName()):
				return True
		return False
	def addLinkTo(self,otherArticleName):
		for linkedArticleName in self.articleLinks:
			if(linkedArticleName == otherArticleName):
				return False
		self.articleLinks.append(otherArticleName)
		return True
	def serialize(self):
		return json.JSONEncoder().encode({"Article" : self.articleName,"links" : self.articleLinks})

class ArticlesController:
	__instance = None
	@staticmethod
	def getInstance():
		if(ArticlesController.__instance == None):
			ArticlesController.__instance = ArticlesController()
			ArticlesController.__instance.deserialize()
		return ArticlesController.__instance
		
	def __init__(self):
		self.articlesList=list()
		self.wikiconnection = HTTPConnection("en.wikipedia.org")
	def downloadText(self,article):
		self.wikiconnection.request("GET","/wiki/"+article.getArticleName())
		articleResponse = self.wikiconnection.getresponse()
		
		print(article.getArticleName(),"request status:",articleResponse.status)
		
		if(articleResponse.status!=200):
			print("Error!")
			quit(1)
		
		return articleResponse.read()
	
	def getArticle(self,name,links=list(),download=False):
		return self.addArticle(name,links,download)
	def getArticlesList(self):
		return self.articlesList
	def addArticle(self,name,links=list(),download=True):
		for article in self.articlesList:
			if(article != None):
				if(article.getArticleName() == name):
					return article
		self.articlesList.append(Article(name,links,download))
		return self.articlesList[len(self.articlesList)-1]
	
	def deserialize(self):
		f = open("db.json","r")
		def __hook_hook(dct):
			ArticlesController.getInstance().__json_hook_ArticleObject(dct)
		json.load(f, object_hook=__hook_hook)
	def __json_hook_ArticleObject(self,dct):
		if 'Article' in dct:
			ArticlesController.getInstance().addArticle(dct['Article'], dct['links'], False)
		return dct
	def serialize(self):
		class ArticleEncoder(json.JSONEncoder):
			def default(self, obj):
				if isinstance(obj, Article):
					return {"Article":obj.getArticleName(), "links":obj.getLinkedArticlesNames()}
				return json.JSONEncoder.default(self, obj)

		out=ArticleEncoder().encode(self.articlesList)
		f = open("db.json", "w")
		f.write(out)

Application().run()
