#!/usr/bin/python

import sys
import io
import re
from http.client import HTTPConnection, HTTPResponse
from html.parser import HTMLParser
from queue import Queue,Empty
from threading import Thread

class Application:
	
	connection = None
	
	def __init__(self):
		ArticlesController.getInstance()
		self.running = True
		self.queue = Queue()

	def isRunning(self):
		return self.running
	def stopRunning(self):
		self.running = False

	def run(self):
		if(len(sys.argv)<3):
			quit(1)
		
		srcArticleName = sys.argv[1].replace(" ","_")
		dstArticleName = sys.argv[2].replace(" ","_")

		self.queue.put( {"src":srcArticleName, "depth":0, "dst":dstArticleName,"route":list()} )
		
		num_worker_threads = 5
		threads=list()
		for i in range(num_worker_threads):
			t = Thread(target=self.worker)
			t.daemon = True
			t.start()
			threads.append(t)
		
		#self.queue.join()
		for thread in threads:
			thread.join()
	
	def search(self, src, depth, dst, route=list()):
		if(len(route)>0):
			print("from", route[len(route)-1],"searching", src,"to",dst)
		else:
			print("searching", src,"to",dst)
		
		myroute = route[:]
		#myroute = copy.deepcopy(route)
		myroute.append(src)
		
		for article in ArticlesController.getInstance().getArticle(src).getLinkedArticlesNames():
			if(article == dst):
				print(myroute, src,"after",depth,"articles")
				self.stopRunning()
				return
		
		for article in ArticlesController.getInstance().getArticle(src).getLinkedArticlesNames():
			self.queue.put( {"src":article, "depth":depth+1, "dst":dst,"route":myroute} )

	def worker(self):
		print("Worker ready")
		while self.running:
			try:
				task = self.queue.get(True,2)
				self.search(task['src'],task['depth'],task['dst'],task['route'])
				self.queue.task_done()
			except Empty:
				print("Worker: no tasks")

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
