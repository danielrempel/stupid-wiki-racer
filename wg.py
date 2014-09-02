#!/usr/bin/python

import sys
import re
from http.client import HTTPConnection
from Article import Article

class Application:
	def __init__(self):
		self.wikiconnection = HTTPConnection("en.wikipedia.org")
	def checkInput(self):
		if(len(sys.argv) < 2):
			print("Usage: ", sys.argv[0], " <artcile name>|<article link>");
			quit(1)
	def parseInput(self):
		linkPattern = re.compile("((http://)|(https://))?en\.wikipedia\.org/wiki/([A-Za-z0-9!@#$%^&*()_+=,./ -])*")
		if(linkPattern.match(sys.argv[1])):
			articleNamePattern = re.compile("([A-Za-z0-9!@$%^&*()_+=,. '-]*)(?:#[A-Za-z_]*)?$")
			self.targetArticleName = articleNamePattern.findall(text)[0]
		else:
			self.targetArticleName = sys.argv[1]
	
	def run(self):
		
		self.checkInput()
		self.parseInput()
		
		self.startArticle = Article(self.wikiconnection, self.targetArticleName)

Application().run()
