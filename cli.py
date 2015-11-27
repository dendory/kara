#
# Command line interface for KARA - (C) 2015 Patrick Lambert - Provided under the MIT License
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
	if len(words) == 0:
		pass
	elif (kara.is_a_term(concepts, words[0]) and len(words) == 1) or (words[0].lower() == 'define' and len(words) > 1): # Define a term
		term = words[0]
		if words[0].lower() == 'define':
			term = words[1]
		kara.add_term(concepts, term)
		data = kara.get_data(concepts, term)
		for key, value in data.items():
			print(str(key) + ": " + str(value))
		relations = kara.get_relations(concepts, term)
		for r in relations:
			print(term + " " + str(r['relation']) + ": " + str(r['name']))
	elif words[0].lower() == 'delete' and len(words) > 1: # Remove a term
		kara.del_term(concepts, words[1])
	elif words[0].lower() == 'load' and len(words) > 1: # Load a data set
		concepts = kara.load_concepts(words[1] + ".json")
		concepts_name = words[1]
		print("Loaded: " + concepts_name)
	elif words[0].lower() == 'import' and len(words) > 1: # Import an additional data set
		concepts.update(kara.load_concepts(words[1] + ".json"))
		print("Imported: " + words[1])
	elif words[0].lower() == 'clear': # Clear the data set
		concepts = {}
		concepts_name = ""
	elif words[0].lower() == 'save': # Save a data set
		if concepts_name == "":
			concepts_name = input("Enter data set name: ")
		kara.save_concepts(concepts, concepts_name + ".json")
		print("Saved: " + concepts_name)
	elif words[0].lower() == 'help': # Basic help text
		print("KARA - The concepts engine")
		print()
		print("Commands available:")
		print("define <term>")
		print("delete <term>")
		print("<term> [relation] [term]")
		print("list [key]")
		print("keys <term>")
		print("load <dataset>")
		print("save [dataset]")
		print("import <dataset>")
		print("<question>?")
		print("quit")
		print()
		print("Example:")
		print("> load solarsystem")
		print("> blue is a color")
		print("> red is a color")
		print("> Earth is a planet")
		print("> Mars clone Earth")
		print("> Earth is blue")
		print("> Mars is red")
		print("> What color is the Earth?")
		print("> save")
		print()
	elif words[0].lower() == 'keys' and len(words) > 1: # Step through each key
		data = kara.get_data(concepts, words[1])
		for key, value in data.items():
			new_value = input(key + " [" + value + "]: ")
			if new_value != '':
				kara.add_data(concepts, words[1], key, new_value)
	elif words[0].lower() == 'list' or words[0].lower() == 'ls': # List concepts
		if len(words) < 2 or words[1].lower() == 'concepts' or words[1].lower() == 'terms':
			terms = kara.get_terms(concepts)
			print(str(terms) + "\nTotal: " + str(len(terms)))
		elif words[1].lower() == 'relations' or words[1].lower() == 'keywords':
			print(str(kara.relations))
			print(str(kara.inverses))
		else:
			keys = kara.get_key(concepts, words[1]) 
			print(str(keys) + "\nTotal: " + str(len(keys)))
	elif words[0].lower() == 'quit' or words[0].lower() == 'exit': # Quit
		if (concepts_name != "" and concepts != kara.load_concepts(concepts_name + ".json")) or (concepts_name == "" and concepts != {}):
			if input("Data set modified. Quit without saving [y/n]? ").lower() == 'y':
				quit(0) 
		else:
			quit(0)
	elif question: # A question was asked
		terms = kara.find_terms(concepts, words)
		if len(terms) == 0:
			print("Ambiguous question: " + str(words))
		elif len(terms) == 1:
			print("Ambiguous question. Only the following term is defined: " + str(terms))
		else:
			print("[" + terms[0] + "] of [" + terms[1] + "]: " + str(kara.find_relation(concepts, terms[0], terms[1])))
	elif 'is not' in q and len(words) > 3: # Remove relation between two terms
		kara.unrelate_term(concepts, str(words[0]), str(words[-1]))
	elif (' clone ' in q or ' copy ' in q) and len(words) > 2: # clone a term
		kara.clone_terms(concepts, str(words[0]), str(words[-1]))
	elif ('=' in q or ':' in q) and len(words) > 1: # Save a key/value pair
		e = q[q.index(words[0])+len(words[0]):].lstrip('\"').lstrip().replace('\"','')
		if ':' in q:
			k = e[0:e.index(':')].rstrip()
			v = e[e.index(':')+1:].lstrip()
		else:
			k = e[0:e.index('=')].rstrip()
			v = e[e.index('=')+1:].lstrip()
		print("[" + k + "]: [" + v + "]")
		kara.add_data(concepts, words[0], k, v)
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
