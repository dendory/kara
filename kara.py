#
# Simple word association script - (C) 2015 Patrick Lambert - Provided under the MIT License
#
import json
import time
import re
import string

relations = ["GREATER THAN", "LESSER THAN", "PART OF", "HAS AS PART", "CONTAINED IN", "CONTAINS", "SAME AS", "IS A", "DEFINES"]
inverses = ["LESSER THAN", "GREATER THAN", "HAS AS PART", "PART OF", "CONTAINS", "CONTAINED IN", "SAME AS", "DEFINES", "IS A"]
types = ["_number", "_person", "_good", "_bad"]

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

def _log(concepts, event): # Log an event
	for concept in concepts:
		if concept["name"] == "_log":
			concept["data"].append({"event": event, "time": _now()})

#
# Main functions
#
def load_concepts(): # Load concepts from file or create blank structure
	try:
		f = open("concepts.json", "r")
		concepts = json.loads(f.read())
		f.close()
		return concepts
	except:
		concepts = [{"name": "_log", "relations": [], "bias": 0, "data": [{"event": "Creation", "time": _now()}]}]
		for t in types:
			concepts.append({"name": t, "relations": [], "bias": 0, "data": []})
		return concepts
	
def save_concepts(concepts): # Save concepts back to file
	f = open("concepts.json", "w")
	f.write(json.dumps(concepts, sort_keys=True, indent=4))
	f.close()

def add_terms(concepts, terms): # Add terms to concepts
	for term in terms:
		if term != "":
			found = False
			for concept in concepts:
				if str(term).lower() == concept["name"]:
					found = True
					concept["bias"] = concept["bias"] + 1  # Increase bias when we find a recurrence
			if not found:
				concepts.append({"name": str(term).lower(), "relations": [], "bias": 0, "data": []})

def list_terms(concepts): # List all terms
	results = []
	for term in concepts:
		results.append(term["name"])
	return results

def check_relation(relation): # Validate a relation
	if str(relation).upper() in relations:
		return True    
	return False

def inverse_relation(relation): # Inverse a relation
	return inverses[relations.index(relation)]

def relate_term(concepts, term1, term2, relation): # Assign a relation between two term
	add_terms(concepts, [term1, term2])
	if check_relation(relation):
		for concept in concepts:
			if concept["name"] == str(term1).lower():
				found = False
				for r in concept["relations"]:
					if str(term2).lower() == r["name"]:
						found = True
				if not found:
					concept["relations"].append({"name": str(term2).lower(), "relation": str(relation).upper()})
			elif concept["name"] == str(term2).lower():
				found = False
				for r in concept["relations"]:
					if str(term1).lower() == r["name"]:
						found = True
				if not found:
					concept["relations"].append({"name": str(term1).lower(), "relation": inverse_relation(relation)})

def relate_terms(concepts, terms, term, relation): # Relate multiple terms to one
	add_terms(concepts, [term])
	add_terms(concepts, terms)
	for t in terms:
		relate_term(concepts, t, term, relation)

def add_type(concepts, term, mytype): # Add a basic type
	if mytype in types:
		for concept in concepts:
			if concept["name"] == term.lower():
				relate_term(concepts, term, mytype, "IS A")

def define_types(concepts): # Define basic types
	for concept in concepts:
		if _is_int(concept["name"]): # Numbers
			add_type(concepts, concept["name"], "_number")
		if concept["name"] == "me" or concept["name"] == "kara": # Person
			add_type(concepts, concept["name"], "_person")
