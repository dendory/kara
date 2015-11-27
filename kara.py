#
# KARA: Concepts engine - (C) 2015 Patrick Lambert - Provided under the MIT License
#
import json
import time
import re
import string
import shlex

version = "0.2"
relations = ["greater", "lesser", "part", "joins", "contained", "contains", "same", "plurial", "singular", "is", "defines"]
inverses = ["lesser", "greater", "joins", "part", "contains", "contained", "same", "singular", "plurial", "defines", "is"]
reserved_terms = ["_number", "_kara"]
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

def _basic_types(concepts, term): # Define basic known types
	if _is_int(term): # Numbers
		concepts[term]["relations"].append({"name": "_number", "relation": "is"})

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
		for t in reserved_terms:
			concepts[t] = {"relations": [], "bias": 0, "data": {}}
		add_data(concepts, "_kara", "creation time", _now())
		add_data(concepts, "_kara", "version", version)
		return concepts
	
def save_concepts(concepts, filename): # Save concepts back to file
	add_data(concepts, "_kara", "last modification time", _now())
	f = open(filename, "w")
	f.write(json.dumps(concepts, sort_keys=True, indent=4))
	f.close()

def clone_terms(concepts, term1, term2, force=False):
	if str(term2).lower() in concepts:
		if str(term1).lower() not in concepts or force:
			add_term(concepts, term1)
			for r in get_relations(concepts, term2):
				relate_term(concepts, term1, r['name'], r['relation'])
			for k, v in get_data(concepts, term2).items():
				add_data(concepts, term1, k, v)
	elif str(term1).lower() in concepts:
		if str(term2).lower() not in concepts or force:
			add_term(concepts, term2)
			for r in get_relations(concepts, term1):
				relate_term(concepts, term2, r['name'], r['relation'])
			for k, v in get_data(concepts, term1).items():
				add_data(concepts, term2, k, v)

def add_term(concepts, term): # Add term to concepts
	if term == "":
		return
	elif str(term).lower() not in concepts:
		concepts[str(term).lower()] = {"relations": [], "bias": 0, "data": {}}
		_basic_types(concepts, str(term).lower())
	else:
		concepts[str(term).lower()]["bias"] = concepts[str(term).lower()]["bias"] + 1  # Increase bias when we find a recurrence

def del_term(concepts, term): # Remove a term
	if str(term).lower() in concepts:
		for c_name, c in concepts.items():
			unrelate_term(concepts, term, c_name)
		del concepts[str(term).lower()]

def get_terms(concepts): # List all terms
	results = []
	for k in concepts.keys():
		results.append(k)
	results.sort()
	return results

def add_data(concepts, term, key, value): # Add key/value pair to term
	if value == '':
		try:
			del concepts[str(term).lower()]["data"][str(key).lower()]
		except:
			pass
	else:
		if not str(term).lower() in concepts:
			add_term(concepts, term)
		concepts[str(term).lower()]["data"][str(key).lower()] = value

def get_data(concepts, term): # Get key/value pairs for a term
	if term in concepts:
		return concepts[str(term).lower()]["data"]
	else:
		return {}

def get_key(concepts, key): # Get values of a key for all terms
	results = []
	for c_name, c in concepts.items():
		if str(key).lower() in c["data"]:
			results.append({c_name: c["data"][str(key).lower()]})
	return results


def check_relation(relation): # Validate a relation
	if str(relation).lower() in relations:
		return True    
	return False

def inverse_relation(relation): # Inverse a relation
	return inverses[relations.index(relation)]

def unrelate_term(concepts, term1, term2): # Remove a relation between two terms
	for r in concepts[str(term1).lower()]["relations"]:
		if r['name'] == str(term2).lower():
			concepts[str(term1).lower()]["relations"].remove({"name": str(term2).lower(), "relation": r['relation']})
	for r in concepts[str(term2).lower()]["relations"]:
		if r['name'] == str(term1).lower():
			concepts[str(term2).lower()]["relations"].remove({"name": str(term1).lower(), "relation": r['relation']})


def relate_term(concepts, term1, term2, relation): # Assign a relation between two term
	if not str(term1).lower() in concepts:
		add_term(concepts, term1)
	if not str(term2).lower() in concepts:
		add_term(concepts, term2)
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
	add_term(concepts, term)
	for t in terms:
		add_term(concepts, t)
	for t in terms:
		relate_term(concepts, t, term, relation)

def get_relations(concepts, term): # Define a concept and its relations
	if str(term).lower() in concepts:
		return concepts[str(term).lower()]["relations"]
	return []

def parse_query(text): # Parse a query and return useful terms
	words = shlex.split(text)
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
