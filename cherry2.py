import cherrypy, os, urllib, json
import tfidf as calculate_tfidf

# improvements to be made: rank the resulting documents, 
# is there a better way than just checking if word appears in document?
# take top words from one document and find which documents relate instead of top words in general

class LinksDemo(object):

	def __init__(self):
		''' function description '''
		self.header = """
			<!doctype html>
			<head>
			<title>Linking test</title>
			</head>
			<body>
			"""

		self.footer = """
			</body>
			</html>
			"""

	def show_corpus(self):
		'''function description'''
		self.documents = """
						<div>Corpus
							<ul>
						"""
		for root, dirs, files in os.walk(os.path.join(os.getcwd(), 'corpus')):
			for file in files:
				if file.endswith('.txt'):
					self.documents += """
									<li>%s</li>
									""" % file
		self.documents += """
						</ul></div>
						"""

	def search_corpus(self, query):
		''' function description '''

		with open('tfidf.json') as scores:
			tfidf = json.load(scores)
			with open(os.path.join(os.getcwd(), 'corpus', query)) as data:
				f = json.load(data)
				top_twenty = []
				i = 0
				while (len(top_twenty) < 20):
					if (tfidf[i][0] in f):
						top_twenty.append(tfidf[i][0])
					i += 1
		
		self.top_twenty = top_twenty

		matching_words = {}
		relevant_docs = []
		for root, dirs, files in os.walk(os.path.join(os.getcwd(), 'corpus')):
			for file in files:
				if (file.endswith('_cleaned.json') and file != query):
					matching_words[file] = []
					file_path = os.path.join('corpus', file)
					with open(file_path) as data:
						stems = json.load(data)
						for stem in stems: #japan =/= japanes
							if (stem in top_twenty):
								if(stem not in matching_words[file]):
									matching_words[file].append(stem)
									if (file not in relevant_docs):
										relevant_docs.append(file)
		self.matching_words = matching_words
		self.relevant_docs = relevant_docs
		print matching_words

	def index(self, query=None):
		html = self.header
		self.show_corpus()
		html += self.documents
		html += """
			<br>
			Click on a document to find related materials.
			</br>
			"""

		html += """<ol>"""
		for root, dirs, files in os.walk(os.path.join(os.getcwd(), 'corpus')):
			for file in files:
				if file.endswith('_cleaned.json'):
					html += """<li><a href='?query=%s'>%s</a></li>""" % (file, file)
		html += """</ol>"""

		if query:
			print query
			#query the corpus and find related documents
			self.search_corpus(query)
			html += """
			<br>
			Here are the linked documents and bolded words are matching
			</br>
			"""
		
			html += """<ul>"""
			for doc in self.relevant_docs:
				html += """<li>%s:""" % doc
				html += """<ol>"""
				for word in self.matching_words[doc]:
					html += """<li>%s</li>""" % word
				html += """</ol></li>"""
			html += """</ul>"""

		html += self.footer
		return html

	index.exposed = True

conf = {
		'/': {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './public'
		}
}



cherrypy.quickstart(LinksDemo(), '/', conf)
