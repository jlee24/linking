import json
import math
import nltk
import operator
import unicodedata

tfidf = {}
in_docs = {}

def findTotals(jdata):
	''' function description '''
	totalDocs = 0
	totalWords = 0
	for fileName in jdata:
		totalDocs += 1
		for word in jdata[fileName]:
			totalWords += 1
	return totalDocs, totalWords

with open('word_frequencies.json') as wordFreqs:
	json_data = json.load(wordFreqs)

	totalDocs, totalWords = findTotals(json_data)
	
	for fileName in json_data:
		for word in json_data[fileName]: 
	 		freq = json_data[fileName][word]
	 		tf = freq/float(totalWords)
			tfidf[word] = tf

	for word in tfidf:
		in_doc = 0
		for fileName in json_data:
			if word in json_data[fileName]:
				in_doc += 1		
				in_docs[word] = in_doc

	for word in in_docs:
		idf = math.log(totalDocs/in_docs[word])
		tfidf[unicodedata.normalize('NFC', word).encode("utf-8")] *= idf

	with open('tfidf.json', 'w') as f:
		sorted_tfidf = sorted(tfidf.items(), key=operator.itemgetter(1), reverse=True)
		json.dump(sorted_tfidf, f, ensure_ascii=False, indent=4, sort_keys=True)