#!/usr/bin/python

from queue import Queue,Empty
from threading import Thread

class StatisticsModule:
	__instance = None
	@staticmethod
	def getInstance():
		if(StatisticsModule.__instance == None):
			StatisticsModule.__instance = StatisticsModule()
		return StatisticsModule.__instance
	
	def __init__(self):
		self.pagesSearched=0
		self.linksSearched=0
		self.queue = Queue()
		
		t = Thread(target=self.worker)
		t.daemon = True
		t.start()
		
	
	def addLinksSearched(self,amount):
		self.queue.put( { "type":0, "amount":amount } )
	
	def getLinksSearched(self):
		return self.linksSearched
	
	def addArticlesSearched(self,amount):
		self.queue.put( { "type":1, "amount":amount } )

	def getArticlesSearched(self):
		return self.pagesSearched

	def getQueue(self):
		return self.queue

	def worker(self):
		empty=0
		while True:
			task = self.queue.get()
			if(task["type"] == 0):
				self.linksSearched += task["amount"]
			else:
				self.pagesSearched += task["amount"]
			self.queue.task_done()
