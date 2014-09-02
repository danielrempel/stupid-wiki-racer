#!/usr/bin/python

from http.client import HTTPConnection, HTTPResponse
from html.parser import HTMLParser

class Article:
	linkedArticles = []
	
	def __init__(self, wikiconnection, name):
		self.name = name.replace(" ", "_")
		self.wikiconnection = wikiconnection
		self.parseArticle()
	
	def getArticleName(self):
		return self.name
	
	def addLinkedArticle(self,article):
		self.linkedArticles.append(article.getArticleName())
	
	def getLinkedArticles(self):
		return self.linkedArticles
	
	def parseArticle(self):
		articleText = self.loadArticleText()
		#print("Article text:\n", articleText.decode("utf-8"))
		articleParser = ArticleParser()
		articleParser.feed(articleText.decode("utf-8"))

	def loadArticleText(self):
		self.wikiconnection.request("GET","/wiki/"+self.name)
		articleResponse = self.wikiconnection.getresponse()
		return articleResponse.read()

class ArticleParser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.divdepth = 0
		self.inContentBlock = False
		self.contentLevel = 0
		self.inP = False
		self.inLink = False
	def handle_starttag(self, tag, attrs):
		# or table.navbox
		# or span#See_also —> ul
		if(tag == "div"):
			self.divdepth += 1
			found = False
			for attr in attrs:
				if((attr[0] == "id")and(attr[1] == "content")):
					self.inContentBlock = True
					self.contentLevel = self.divdepth
		if((tag == "p")and(self.inContentBlock)):
			self.inP = True
		if((tag == "a")and(self.inP)):
			self.inLink = True
			print("Link attrs: ", attrs)
			# TODO: get an href from here, pass it further
			
	def handle_endtag(self, tag):
		if(tag == "div"):
			if(self.divdepth == self.contentLevel):
				self.inContentBlock = False
			self.divdepth -= 1
		if(tag == "p"):
			self.inP = False
		if(tag == "a"):
			self.inLink = False
