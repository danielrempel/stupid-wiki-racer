#!/usr/bin/python

import sys
import io
import re
from http.client import HTTPConnection, HTTPResponse
from html.parser import HTMLParser

class Application:
	
	connection = None
	
	def __init__(self):
		ArticlesController.getInstance()

	def run(self):
		if(len(sys.argv)<3):
			quit(1)
		
		srcArticleName = sys.argv[1].replace(" ","_")
		dstArticleName = sys.argv[2].replace(" ","_")

		i=0
		print("iteration", i+1,"staring")
		while(not self.search(srcArticleName,i,dstArticleName)):
			i+=1
			print("iteration", i+1,"staring")
		print(srcArticleName)
		print()
	
	def search(self, src, depth, dst):
		ArticlesController.getInstance().getArticle(src)
		for article in ArticlesController.getInstance().getArticle(src).getLinkedArticlesNames():
			if(article == dst):
				print(article)
				return True
		if(depth>0):
			for article in ArticlesController.getInstance().getArticle(src).getLinkedArticlesNames():
				if(self.search(article,depth-1,dst) == True):
					print(article)
					return True
		return False

class Article:
	def __init__(self,articleName,articleLinks=list()):
		self.articleName = articleName
		self.articleLinks = articleLinks
		self.populateArticle()
	def populateArticle(self):
		wikiconnection = HTTPConnection("en.wikipedia.org")
		wikiconnection.request("GET","/wiki/"+self.articleName)
		articleResponse = wikiconnection.getresponse()
		print(self.articleName,"request status:",articleResponse.status)
		if(articleResponse.status!=200):
			print("Error!")
			quit(1)
		articleText = articleResponse.read()
		
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

	def getArticleName(self):
		return self.articleName
	def getLinkedArticlesNames(self):
		return self.articleLinks
	def addLinkTo(self,otherArticleName):
		for linkedArticleName in self.articleLinks:
			if(linkedArticleName == otherArticleName):
				return False
		self.articleLinks.append(otherArticleName)
		return True

class ArticlesController:
	__instance = None
	@staticmethod
	def getInstance():
		if(ArticlesController.__instance == None):
			ArticlesController.__instance = ArticlesController()
		return ArticlesController.__instance
		
	def __init__(self):
		self.articlesList=list()
	def getArticle(self,name,links=list()):
		return self.addArticle(name,links)
	def getArticlesList(self):
		return self.articlesList
	def addArticle(self,name,links=list()):
		for article in self.articlesList:
			if(article != None):
				if(article.getArticleName() == name):
					return article
		self.articlesList.append(Article(name,links))
		return self.articlesList[len(self.articlesList)-1]

Application().run()
