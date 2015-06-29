#
# Command line interface for Kara - (C) 2015 Patrick Lambert - Provided under the MIT License
#
import kara

concepts = {}
concepts_name = ""

while True:
	q = input("> ")
	words = kara.parse_query(q)
	question = False
	if len(q) > 1 and q[-1] == '?':
		question = True
	if (kara.is_a_term(concepts, words[0]) and len(words) == 1) or (words[0].lower() == 'define' and len(words) > 1): # Define a term
		term = words[0]
		if words[0].lower() == 'define':
			term = words[1]
		kara.add_terms(concepts, [term])
		relations = kara.get_relations(concepts, term)
		for r in relations:
			print(term + " " + r['relation'] + ": " + r['name'])
	elif words[0].lower() == 'load' and len(words) > 1: # Load a data set
		concepts = kara.load_concepts(words[1] + ".json")
		concepts_name = words[1]
		print("Loaded: " + concepts_name)
	elif words[0].lower() == 'save': # Save a data set
		if concepts_name == "":
			concepts_name = input("Enter data set name: ")
		kara.save_concepts(concepts, concepts_name + ".json")
		print("Saved: " + concepts_name)
	elif words[0].lower() == 'list': # List concepts
		if len(words) < 2 or words[1].lower() == 'concepts' or words[1].lower() == 'terms':
			print(kara.get_terms(concepts))
		elif words[1].lower() == 'relations' or words[1].lower() == 'keywords':
			print(str(kara.relations))
			print(str(kara.inverses))
	elif words[0].lower() == 'quit' or words[0].lower() == 'exit': # Quit
		if (concepts_name != "" and concepts != kara.load_concepts(concepts_name + ".json")) or (concepts_name == "" and concepts != {}):
			if input("Data set modified. Quit without saving [y/n]? ").lower() == 'y':
				quit(0) 
		else:
			quit(0)
	elif question: # A question was asked
		terms = kara.find_terms(concepts, words)
		if len(terms) < 2:
			print("Ambiguous question. Only the following term is defined: " + str(terms))
		else:
			print("[" + terms[0] + "] of [" + terms[1] + "]: " + kara.find_relation(concepts, terms[0], terms[1]))
	else: # Try to define a relationship
		found = False
		for r in kara.relations:
			if r in q:
				print("[" + words[0] + "] " + r + " [" + words[-1] + "]")
				kara.relate_term(concepts, str(words[0]), str(words[-1]), r)
				found = True
			if found:
				break
		if not found:
			print("Unknown statement: " + str(words))
