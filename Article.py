import re
from http.client import HTTPConnection, HTTPResponse
from html.parser import HTMLParser

class Article:
	def __init__(self,articleName):
		self.articleName = articleName
		self.articleLinks = list()
		self.populateArticle()
		
		self.checked=False
	def populateArticle(self):
		wikiconnection = HTTPConnection("en.wikipedia.org")
		wikiconnection.request("GET","/wiki/"+self.articleName)
		articleResponse = wikiconnection.getresponse()
		if(articleResponse.status!=200):
			print("Error! Article response status is", articleResponse.status)
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
								if(self.checkLink(cleanLink)):
									self.parentArticle.addLinkTo(cleanLink)
			def clearLink(self,link):
				linkCleaner = re.compile("/wiki/([A-Za-z0-9:;!@$%^&*()_+=.,/ -]*)[A-Za-z0-9:;!@#$%^&*()_+=.,/ -]*")
				return linkCleaner.findall(link)[0]
			def checkLink(self,link):
				specialRE = re.compile("(Special|Help|File|Portal|Wikipedia|Template|Template_talk|Talk):[A-Za-z0-9;!@#$%^&*()_+=.,/ -]*")
				if(specialRE.match(link)):
					return False
				return not link == self.parentArticle.getArticleName()
		
		articleParser = ArticleParser(self)
		articleParser.feed(articleText.decode("utf-8"))

	def wasChecked(self):
		self.checked=True
	def isChecked(self):
		return self.checked

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
