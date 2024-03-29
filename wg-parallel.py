#!/usr/bin/python

import sys
import io
from queue import Queue,Empty
from threading import Thread
from Article import Article
from ArticlesController import ArticlesController
from StatisticsModule import StatisticsModule
import time

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
		
		start_time = time.time()
		
		srcArticleName = sys.argv[1].replace(" ","_")
		dstArticleName = sys.argv[2].replace(" ","_")

		self.queue.put( {"src":srcArticleName, "depth":1, "dst":dstArticleName,"route":list()} )
		
		num_worker_threads = 5
		threads=list()
		for i in range(num_worker_threads):
			t = Thread(target=self.worker)
			t.daemon = True
			t.start()
			threads.append(t)

		for thread in threads:
			thread.join()
		
		StatisticsModule.getInstance().getQueue().join()
		
		print("--- {} threads : {} articles : {} links : {} seconds ---".format(num_worker_threads, StatisticsModule.getInstance().getArticlesSearched(), StatisticsModule.getInstance().getLinksSearched(), time.time() - start_time))
	
	def search(self, src, depth, dst, route=list()):
		if(ArticlesController.getInstance().getArticle(src).isChecked()):
			return
		else:
			ArticlesController.getInstance().getArticle(src).wasChecked()
		
		StatisticsModule.getInstance().addArticlesSearched(1)
		
		if(len(route)>0):
			print("Level",depth,"from", route[len(route)-1],"searching", src,"to",dst)
		else:
			print("Level",depth,"searching", src,"to",dst)
		
		myroute = route[:]
		myroute.append(src)
		
		for article in ArticlesController.getInstance().getArticle(src).getLinkedArticlesNames():
			StatisticsModule.getInstance().addLinksSearched(1)
			if(article == dst):
				print(myroute, dst,"after",depth,"articles")
				self.stopRunning()
				return
		
		for article in ArticlesController.getInstance().getArticle(src).getLinkedArticlesNames():
			self.queue.put( {"src":article, "depth":depth+1, "dst":dst,"route":myroute} )

	def worker(self):
		print("Worker ready")
		while self.running:
			try:
				task = self.queue.get(True,1)
				self.search(task['src'],task['depth'],task['dst'],task['route'])
				self.queue.task_done()
			except Empty:
				print("Worker: no tasks")

Application().run()
