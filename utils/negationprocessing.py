#negation map building stuff
import os
import spacy
import scispacy
from spacy import displacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
from negspacy.negation import Negex
from utils.preprocess import *

def neg_model(nlp_model):
    nlp = spacy.load(nlp_model, disable = ['parser'])
    nlp.add_pipe('sentencizer')
    
    #negex = Negex(nlp, )
    
    nlp.add_pipe("negex", config={"ent_types": ["PERSON", "ORG", "DISEASE", "FINDING"]})
    return nlp
"""
Negspacy sets a new attribute e._.negex to True if a negative concept is encountered
"""
def negation_handling(nlp_model, note, neg_model):
    results = []
    #nlp = neg_model(nlp_model) 
    note = note.split(".") #sentence tokenizing based on delimeter 
    note = [n.strip() for n in note] #removing extra spaces at the begining and end of sentence
    for t in note:
        doc = nlp_model(t)
        for e in doc.ents:
            rs = str(e._.negex)
            if rs == "True": 
                results.append(e.text)
    return results

def extract_negation_per_report(filepath):
    orig_sentences = extract_sentences(filepath)
    for sent in orig_sentences:                    
        neg_findings = classify_negation(sent, nlp0, neg_model, nlpmodel)
      #  print(sent,neg_findings)
        
def extract_negations_list(orig_sentences):
    for sent in orig_sentences:                    
        neg_findings = classify_negation(sent, nlp0, neg_model, nlpmodel)
       # print(sent,"\t",neg_findings)

        
def extract_neg_map(main_path,nlp0,neg_model,nlpmodel):
    
   
    negMap={}
    for root, dirs, files in os.walk(main_path, topdown=False, onerror=None, followlinks=True):
        for filename in files:
            if filename != '.DS_Store':
                filepath = os.path.join(root, filename)
                orig_sentences = extract_sentences(filepath)
                
                for sent in orig_sentences:                    
                    neg_findings = classify_negation(sent, nlp0, neg_model, nlpmodel)
                    for negfinding in neg_findings:
                       # print(negfinding,"->",sent)
                        if negfinding not in negMap:
                            sentset=set()
                        else:
                            sentset=negMap[negfinding]
                        sentset.add(sent)
                        negMap[negfinding]=sentset
    return negMap

def find_nearest_match(actualfinding, detected_findings):
    possiblefindings=[]
    for candfinding in detected_findings:
        if (candfinding==actualfinding):
            possiblefindings.append(candfinding)
            return possiblefindings
        else:
            if (candfinding in actualfinding) or (actualfinding in candfinding):
                possiblefindings.append(candfinding)
    return possiblefindings
#this is because the neg_map is indexed by finding keys derived from negspacy
#whereas the problem_map is indexed by finding keys derived from the reports.csv (i.e. provided as ground truth)
#since the two have to match, we map the negspacy findings to the nearest actual findings and vice versa
def map_findings(problem_map,neg_map):
    pos_map = {}
    definite_negmap={}
    for finding in problem_map:
        if (len(problem_map[finding])>0):
            #print(finding)
            all_sentences=problem_map[finding] #F1->{s1,s2,s3,s4}
            if (finding not in neg_map):
                #means the finding may be a morphed version
                nearestfindings=find_nearest_match(finding,neg_map.keys())
           # print(all_sentences)
                #if (len(nearestfindings)>0):
                   # print("neasrest matche = ",finding,nearestfindings)
            else:
                nearestfindings=set()
                nearestfindings.add(finding)


           # print("neasrest ",finding,nearestfindings)
            if (len(nearestfindings)>0):
                for nearestfinding in nearestfindings:
                    cand_neg_sentences=neg_map[nearestfinding]
                    
                    neg_sentences=[]
                    pos_sentences=[]
                    for sent in all_sentences:
                        if sent in cand_neg_sentences:
                            neg_sentences.append(sent)
                        else:
                            pos_sentences.append(sent)
                    if (len(neg_sentences)>0):
                      #  print("Negative sentences for ", finding,nearestfinding)
                      #  print(len(neg_sentences))
                        definite_negmap[finding]=neg_sentences
                        pos_map[finding] = pos_sentences
                    
    return definite_negmap, pos_map

def lemmatize(note, nlp):
    doc = nlp(note)
    lemNote = [wd.lemma_ for wd in doc]
    return " ".join(lemNote)

def classify_negation(sent,nlp0,neg_model,nlpmodel):
   
    lem_clinical_note= lemmatize(sent, nlp0)
    results = negation_handling(nlpmodel, lem_clinical_note, neg_model)
   # if (len(results)>0):
      #  print(results,sent)
    return results    
nlp0 = spacy.load("en_core_sci_sm")
nlpmodel = neg_model("en_ner_bc5cdr_md") 