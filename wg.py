#!/usr/bin/python

import sys
import io
from Article import Article
from ArticlesController import ArticlesController

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
		
		print("After checking",ArticlesController.getInstance().getArticlesCheckedCount(),"articles")
	
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

Application().run()
