#
# Concepts engine - (C) 2015 Patrick Lambert - Provided under the MIT License
#
import json
import time
import re
import string

relations = ["greater", "lesser", "part", "joins", "contained", "contains", "same", "is", "defines", "plurial", "singular"]
inverses = ["lesser", "greater", "joins", "part", "contains", "contained", "same", "defines", "is", "singular", "plurial"]
types = ["_number", "_person", "_good", "_bad"]
ignore_terms = ["and", "or", "can", "you", "i", "how", "why", "when", "what", "which", "a", "the", "than", "of", "my", "your"]

#
# Utility functions
#
def _is_int(num): # Check if a number
	try:
		int(num)
		return True
	except ValueError:
		return False

def _now(): # Current unixtime
	return int(time.time())

def _split_words(text): # Split sentence into words
	exclude = set(string.punctuation)
	text = ''.join(ch for ch in text if ch not in exclude)
	return re.split(' |\n', text)

def _basic_types(concepts, term): # Define basic known types
	if _is_int(term): # Numbers
		concepts[term]["relations"].append({"name": "_number", "relation": "is"})
	if term == "me" or term == "kara": # Person
		concepts[term]["relations"].append({"name": "_person", "relation": "is"})

def _remove_duplicates(seq): # Remove duplicates from a list
	seen = set()
	seen_add = seen.add
	return [ x for x in seq if not (x in seen or seen_add(x))]
#
# Main functions
#
def load_concepts(filename): # Load concepts from file or create blank structure
	concepts = {}
	try:
		f = open(filename, "r")
		concepts = json.loads(f.read())
		f.close()
		return concepts
	except:
		for t in types:
			concepts[t] = {"relations": [], "bias": 0, "data": []}
		return concepts
	
def save_concepts(concepts, filename): # Save concepts back to file
	f = open(filename, "w")
	f.write(json.dumps(concepts, sort_keys=True, indent=4))
	f.close()

def add_terms(concepts, terms): # Add terms to concepts
	for term in terms:
		if term != "":
			if str(term).lower() not in concepts:
				concepts[str(term).lower()] = {"relations": [], "bias": 0, "data": []}
				_basic_types(concepts, str(term).lower())
			else:
				concepts[str(term).lower()]["bias"] = concepts[str(term).lower()]["bias"] + 1  # Increase bias when we find a recurrence

def get_terms(concepts): # List all terms
	results = []
	for k in concepts.keys():
		results.append(k)
	results.sort()
	return results

def check_relation(relation): # Validate a relation
	if str(relation).lower() in relations:
		return True    
	return False

def inverse_relation(relation): # Inverse a relation
	return inverses[relations.index(relation)]

def relate_term(concepts, term1, term2, relation): # Assign a relation between two term
	if not str(term1).lower() in concepts or not str(term2).lower() in concepts:
		add_terms(concepts, [term1, term2])
	if check_relation(relation):
		found = False
		for r in concepts[str(term1).lower()]["relations"]:
			if str(term2).lower() == r["name"]:
				found = True
		if not found:
			concepts[str(term1).lower()]["relations"].append({"name": str(term2).lower(), "relation": relation})
		found = False
		for r in concepts[str(term2).lower()]["relations"]:
			if str(term1).lower() == r["name"]:
				found = True
		if not found:
			concepts[str(term2).lower()]["relations"].append({"name": str(term1).lower(), "relation": inverse_relation(relation)})

def relate_terms(concepts, terms, term, relation): # Relate multiple terms to one
	add_terms(concepts, [term])
	add_terms(concepts, terms)
	for t in terms:
		relate_term(concepts, t, term, relation)

def get_relations(concepts, term): # Define a concept and its relations
	if str(term).lower() in concepts:
		return concepts[str(term).lower()]["relations"]
	return []

def parse_query(text): # Parse a query and return useful terms
	words = _split_words(text)
	for t in ignore_terms:
		words = [x for x in words if x.lower() != t]
	return words

def is_a_term(concepts, term): # Check if a term is defined
	if str(term).lower() in concepts:
		return True
	return False

def find_terms(concepts, words): # find defined terms in a series of words
	results = []
	for word in words:
		if str(word).lower() in concepts:
			results.append(word)
	return results

def find_relation(concepts, term1, term2): # Find the relation between two terms
	results = []
	if not str(term1).lower() in concepts or not str(term2).lower() in concepts:
		return ["_undefined"]
	for r in concepts[str(term2).lower()]["relations"]: # 1st generation relation
		if r["name"] == str(term1).lower():
			results.append(r["relation"])
		for x in concepts[r["name"]]["relations"]: # 2nd generation relation
			if x["name"] == str(term1).lower():
				results.append(r["name"])
			for y in concepts[x["name"]]["relations"]: # 3rd generation relation
				if y["name"] == str(term1).lower():
					results.append(x["name"])
	return _remove_duplicates(results)
