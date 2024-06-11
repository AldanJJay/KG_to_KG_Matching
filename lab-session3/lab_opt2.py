########## TASK B.1 ##########
# %% Function to find common elements in two lists
def find_common_elements(listA, listB):
    # Find common elements using set intersection
    common_elements = list(set(listA).intersection(set(listB)))
    return common_elements

# %% Example usage
listA = ["pizza", "tomato sauce", "pepperoni", "restaurant"]
listB = ["pizza", "tomato", "peperone", "restaurant"]
listC = find_common_elements(listA, listB)
print(listC)  # Output: ["pizza", "restaurant"]

# %%
from Levenshtein import ratio

def find_similar_elements(listA, listB, similarity_threshold=0.8):
    similar_elements = []
    for a in listA:
        for b in listB:
            similarity = ratio(a, b)
            if similarity >= similarity_threshold:
                similar_elements.append((a, b, similarity))
    return similar_elements

# %% Example usage
listA = ["pizza", "tomato sauce", "pepperoni", "restaurant"]
listB = ["pizza", "tomato", "peperone", "restaurant"]
similar_elements = find_similar_elements(listA, listB)
print(similar_elements)
# Output: [('pizza', 'pizza', 1.0), ('restaurant', 'restaurant', 1.0)]

# %%
from owlready2 import get_ontology

def extract_entity_labels(ontology_path):
    ontology = get_ontology(ontology_path).load()
    entities = []
    for entity in ontology.classes():
        labels = entity.label if entity.label else [entity.name]
        entities.append((entity.iri, labels))
    return entities

def compare_ontologies(ontology_path1, ontology_path2, similarity_threshold=0.8):
    entities1 = extract_entity_labels(ontology_path1)
    entities2 = extract_entity_labels(ontology_path2)
    
    common_entities = []
    similar_entities = []
    
    for uri1, labels1 in entities1:
        for uri2, labels2 in entities2:
            for label1 in labels1:
                for label2 in labels2:
                    similarity = ratio(label1, label2)
                    if similarity >= similarity_threshold:
                        similar_entities.append((uri1, label1, uri2, label2, similarity))
                        if similarity == 1.0:
                            common_entities.append((uri1, uri2))
    
    return common_entities, similar_entities

# %% Example usage with ontology paths
ontology_path1 = "data/human.owl"
ontology_path2 = "data/mouse.owl"

common_entities, similar_entities = compare_ontologies(ontology_path1, ontology_path2)
print("Common Entities:", common_entities)
print("Similar Entities:", similar_entities)

########## TASK B.2 ##########
# %%
from owlready2 import *
from rdflib import Graph, Namespace, URIRef, Literal
from Levenshtein import ratio

# Define a threshold for lexical similarity
SIMILARITY_THRESHOLD = 0.8

# Load ontologies
def load_ontology(file_path):
    return get_ontology(file_path).load()

# Extract entities and their labels from the ontology
def extract_entities(ontology):
    classes = []
    properties = []
    individuals = []
    
    for entity in ontology.classes():
        labels = entity.label if entity.label else [entity.name]
        classes.append((entity.iri, labels))
        
    for entity in ontology.properties():
        labels = entity.label if entity.label else [entity.name]
        properties.append((entity.iri, labels))
        
    for entity in ontology.individuals():
        labels = entity.label if entity.label else [entity.name]
        individuals.append((entity.iri, labels))
        
    return classes, properties, individuals

# Compute lexical similarity and find equivalences
def find_equivalences(entities1, entities2):
    equivalences = []
    for uri1, labels1 in entities1:
        for uri2, labels2 in entities2:
            for label1 in labels1:
                for label2 in labels2:
                    similarity = ratio(label1, label2)
                    if similarity >= SIMILARITY_THRESHOLD:
                        equivalences.append((uri1, uri2, similarity))
    return equivalences

# Create RDF triples for equivalences
def create_rdf_triples(class_equivalences, property_equivalences, instance_equivalences, namespace1, namespace2):
    g = Graph()
    ns1 = Namespace(namespace1)
    ns2 = Namespace(namespace2)
    
    for uri1, uri2, similarity in class_equivalences:
        g.add((URIRef(uri1), URIRef('http://www.w3.org/2002/07/owl#equivalentClass'), URIRef(uri2)))
    
    for uri1, uri2, similarity in property_equivalences:
        g.add((URIRef(uri1), URIRef('http://www.w3.org/2002/07/owl#equivalentProperty'), URIRef(uri2)))
    
    for uri1, uri2, similarity in instance_equivalences:
        g.add((URIRef(uri1), URIRef('http://www.w3.org/2002/07/owl#sameAs'), URIRef(uri2)))
    
    return g

# Save RDF triples to Turtle format
def save_rdf_triples(graph, output_file):
    graph.serialize(destination=output_file, format='turtle')

# Main function to run the lexical matcher
def lexical_matcher(ontology_file1, ontology_file2, output_file):
    ontology1 = load_ontology(ontology_file1)
    ontology2 = load_ontology(ontology_file2)
    
    classes1, properties1, individuals1 = extract_entities(ontology1)
    classes2, properties2, individuals2 = extract_entities(ontology2)
    
    class_equivalences = find_equivalences(classes1, classes2)
    property_equivalences = find_equivalences(properties1, properties2)
    instance_equivalences = find_equivalences(individuals1, individuals2)
    
    graph = create_rdf_triples(class_equivalences, property_equivalences, instance_equivalences, ontology1.base_iri, ontology2.base_iri)
    
    save_rdf_triples(graph, output_file)
    print(f"Alignments saved to {output_file}")

# %%
# Example usage
ontology_file1 = "data/human.owl"
ontology_file2 = "data/mouse.owl"
output_file = "data/aldan-human-mouse.ttl"

lexical_matcher(ontology_file1, ontology_file2, output_file)

########## TASK B.3 ##########
# DONE!

########## TASK B.4 ##########
# %%
def compareWithReference(reference_mappings_file, system_mappings_file):
    ref_mappings = Graph()
    ref_mappings.parse(reference_mappings_file, format="ttl")
    
    system_mappings = Graph()
    system_mappings.parse(system_mappings_file, format="ttl")
    
    
    #We calculate precision and recall via true positives, false positives and false negatives
    #https://en.wikipedia.org/wiki/Precision_and_recall        
    tp=0
    fp=0
    fn=0
    
    for t in system_mappings:
        if t in ref_mappings:
            tp+=1
        else:
            fp+=1

    
    for t in ref_mappings:
        if not t in system_mappings:
            fn+=1
            
            
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f_score = (2*precision*recall)/(precision+recall)
    #print(tp, tp2)
    #print(fp)
    #print(fn)
    print("Comparing '" + system_mappings_file + "' with '" + reference_mappings_file)
    print("\tPrecision: " + str(precision))
    print("\tRecall: " + str(recall))
    print("\tF-Score: " + str(f_score))
# %%
reference_mappings="data/confOf-ekaw-reference-mappings.ttl"
system_mappings="data/aldan-confOf-ekaw.ttl"

#P, R, and F can only be obtained if a reference alignment exists.    
compareWithReference(reference_mappings, system_mappings)

# For the lab you should compare, for example, 
# cmt-confOf-reference.ttl with the cmt-confOf-your-system.ttl you generate.
# compareWithReference("cmt-confOf-reference.ttl", "cmt-confOf-your-system.ttl")
# %%