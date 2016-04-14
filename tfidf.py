import sys
import json
import math
import nltk
import operator
import string
import os
import unicodedata
import re

from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

token_dict = {}
stemmer = PorterStemmer()

def get_tokens(file):
	''' function description '''
	with open(file, 'r') as file_name:
		text = file_name.read()
		lowers = text.lower()
		no_punctuation = lowers.translate(None, string.punctuation)
		tokens = nltk.word_tokenize(no_punctuation)
		return tokens

def stem_tokens(tokens, stemmer):
	''' function description '''
	stemmed = []
	for item in tokens:
		stemmed.append(stemmer.stem(item))
	return stemmed

def clean_corpus_files(corpus):
	''' function description '''
	file_names = {}
	for root, dirs, files in os.walk(os.path.join(os.getcwd(), corpus)):
		for file in files:
			if file.endswith('.txt'):
				file_path = os.path.join(corpus, file)
				tokens = get_tokens(file_path)

				filler_words = ["uh", "um", "uhh", "umm", "er", "eh", "etc", "inaudible", "engelbart", "doug"]

				for i in range(0, len(tokens)):
					token = re.sub("[^A-Za-z]", "", tokens[i]) 
					tokens[i] = token.decode('utf-8')

				stop_words = stopwords.words('english');
				for i in range(0, len(stopwords.words('english'))):
					stop_words[i] = stopwords.words('english')[i].decode('utf-8')
				
				filtered = [w for w in tokens if not (w in filler_words or w in stop_words)]
				stemmed = stem_tokens(filtered, stemmer)
				count = Counter(stemmed)

				for key in count.keys():
					count[key.encode('utf-8')] = count.pop(key)

				file_names[file] = count

				new_file = os.path.abspath("corpus/%s_cleaned.json" % file.replace('.txt', ''))
				with open(new_file, 'w') as cleaned_file:
					for i in range(0, len(stemmed)):
						stemmed[i] = stemmed[i].encode("utf-8")
					json.dump(stemmed, cleaned_file, ensure_ascii=False, encoding="utf-8", sort_keys=True)
	
	with open('word_frequencies.json', 'w') as f:
		json.dump(file_names, f, ensure_ascii=False, sort_keys=True, indent=4)

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

def calculate_tfidf():
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

def main():
	clean_corpus_files('corpus')
	calculate_tfidf()

if __name__ == '__main__':
	main()