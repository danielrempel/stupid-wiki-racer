from Article import Article

class ArticlesController:	
	__instance = None
	@staticmethod
	def getInstance():
		if(ArticlesController.__instance == None):
			ArticlesController.__instance = ArticlesController()
		return ArticlesController.__instance
		
	def __init__(self):
		self.articlesList=list()
		
		self.articlesChecked=0
	def getArticle(self,name,links=list()):
		return self.addArticle(name,links)
	def getArticlesList(self):
		return self.articlesList
	def addArticle(self,name,links=list()):
		for article in self.articlesList:
			if(article != None):
				if(article.getArticleName() == name):
					return article
		self.articlesChecked+=1
		self.articlesList.append(Article(name,links))
		return self.articlesList[len(self.articlesList)-1]
	
	def getArticlesCheckedCount(self):
		return self.articlesChecked
