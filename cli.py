import kara

concepts = kara.load_concepts()

kara.add_terms(concepts, kara._split_words("test me")) # Add terns
kara.relate_terms(concepts, kara._split_words("hair stomach finger bone skin toe foot"), "body", "PART OF") # Define terms
print(kara.list_terms(concepts)) # Print a list of terms
kara.define_types(concepts) # Basic type definitions

kara.save_concepts(concepts)
