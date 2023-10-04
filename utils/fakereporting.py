import numpy as np
import pandas as pd
import os

#from utils.preprocess import extract_findings
from utils.preprocess import *

# takes overall list of findings from original Indiana dataset & compares it with the findings in the current report
# looks for intersections, ensures that only non-overlapping findings are added
def extract_nonoverlapping_findings(findingMap, findings,problem_map):
    nonoverlap_findings=[]
    for finding in findings:
        if (finding not in findingMap) and (finding in problem_map) and (len(problem_map[finding])>0):
            nonoverlap_findings.append(finding)
    return nonoverlap_findings

 #pick a random finding from this list of nonoverlap_findings
def pick_finding(nonoverlap_findings):
    rand_index = np.random.randint(0, len(nonoverlap_findings))
    rand_finding=nonoverlap_findings[rand_index]
    return rand_finding

def pick_random_sentence(orig_sentences,possible_sentences):
    found=False
    if possible_sentences is None:
        return None
    else: 
        while (not found):
            rand_index2 = np.random.randint(0, len(possible_sentences))
            rand_sentence=possible_sentences[rand_index2]
            if rand_sentence not in orig_sentences:
                found=True
        return rand_sentence


def add_random_finding(orig_sentences,process_count,report_to_finding_to_sentencesMap,real_sentenceMap, fake_sentencemap,findings,filename_map,filename,problem_map):
    #make a list of findings to add that is not already present in this report
    nonoverlapping_findings=extract_nonoverlapping_findings(report_to_finding_to_sentencesMap[filename], findings,problem_map)
   #pick a random fiding from that list
   # print("Non overlapping findings ",nonoverlapping_findings)
    rand_finding=pick_finding(nonoverlapping_findings)
    #see what sentences are possible to add for that random finding
    possible_sentences=list(problem_map[rand_finding]) # get list of sentences associated with random finding
   #Pick a sentence from this list. mark this as a fake sentence. Make the finding as the fake finding
    #the real sentence map is the original sentences.
    #the fake sentence map is the new sentence found
    #print("Possible sentences = ",rand_finding, possible_sentences)
    rand_sentence=pick_random_sentence(orig_sentences,possible_sentences)
    fake_findingsmap={}
    fake_findingsmap[rand_finding]=rand_sentence
    fake_sentencemap[filename]=fake_findingsmap
    real_sentenceMap[filename]=report_to_finding_to_sentencesMap[filename]
    affectedfinding=[]
    affectedfinding.append(rand_finding)
  #  print("orig=",orig_sentences)
   # print(rand_sentence)
    copysentences=orig_sentences.copy()
    copysentences.append(rand_sentence)
    process_count+=1
    
    return copysentences,process_count,real_sentenceMap,fake_sentencemap,None,rand_sentence,affectedfinding

def remove_sentence_with_finding(findingMap,deleted_sentence):
    
    newfindingmap=findingMap.copy()
    affectedfinding=[]
    for finding in findingMap:
        sentences=findingMap[finding]
      
        if deleted_sentence in sentences:
            affectedfinding.append(finding)
           # print(finding,deleted_sentence,sentences)
            if (len(sentences)==1):
                #remove the finding altogether
                
                del newfindingmap[finding]
                
            else:
                revisedsentences=sentences.copy()
                revisedsentences.remove(deleted_sentence)
               # for sent in sentences:
                 #   if (not (deleted_sentence==sent)):
                  #      revisedsentences.add(sent)
                newfindingmap[finding]=revisedsentences
    return newfindingmap,affectedfinding

# takes a set of sentences & removes one of them
def remove_random_finding(orig_sentences,process_count,report_to_finding_to_sentencesMap,real_sentenceMap,fake_sentenceMap,findings=None,filename_map=None,filename=None,problem_map=None):
    #pick a random sentence to remove and remove its associated finding
    rand_index = np.random.randint(0, len(orig_sentences))
    copy_sentences=orig_sentences.copy()
    deleted_sentence=copy_sentences[rand_index] 
    del copy_sentences[rand_index] 
    process_count+=1
    
    findingMap=report_to_finding_to_sentencesMap[filename]
    #remove all findings associated with the deleted_sentence and remove the deleted_sentence itself
    newfindingMap,affectedfinding=remove_sentence_with_finding(findingMap,deleted_sentence)
    fake_sentenceMap[filename]={}
    real_sentenceMap[filename]=newfindingMap
    return copy_sentences,process_count,real_sentenceMap,fake_sentenceMap,deleted_sentence,None,affectedfinding





# exchange the findings between added and removed
def exchange_finding(orig_sentences,process_count,report_to_finding_to_sentencesMap,real_sentenceMap,fake_sentencemap,findings,filename_map,filename,problem_map):
    modif_sentences,process_count,real_sentenceMap,fake_sentencemap,deleted_sentence1,added_sentence1,affectedfindinglist1=remove_random_finding(orig_sentences,process_count,report_to_finding_to_sentencesMap,real_sentenceMap,fake_sentencemap,findings,filename_map,filename,problem_map)
    modif_sentences,process_count,real_sentenceMap,fake_sentencemap,deleted_sentence2,added_sentence2,affectedfindinglist2= add_random_finding(modif_sentences,process_count,report_to_finding_to_sentencesMap,real_sentenceMap,fake_sentencemap,findings,filename_map,filename,problem_map)
    for finding in affectedfindinglist2:
        affectedfindinglist1.append(finding)
    return modif_sentences,process_count,real_sentenceMap,fake_sentencemap,deleted_sentence1,added_sentence2,affectedfindinglist1

def isfinding_present(findings, orig_sentences):
    presence_map={}
    for finding in findings:
        for sent in orig_sentences:
            if finding in sent:
                presence_map[finding]=sent
    return presence_map

#only one finding exchanged
#need to ensure the sentence being exchanged is not already present
#1 Pick possible findings to replace in the sentences from the neg-map list since those findings have a pos-map exchange list
# Stop as soon as a possible finding replacement is found
#2. Check if the matching sentence is in the pos_map, then replace it with a random sentence from the neg-Map
#3. Do vice versa if the mathcing sentgence is in the neg-map
#4. If it is neither, and no other findings is matching, leave the sentences in their original form.
# So this method may or may not modify a report

def reverse_finding(orig_sentences,process_count,report_to_finding_to_sentencesMap,
                    real_sentenceMap,fake_sentencemap,negfinding_map, filename_map,filename,posfinding_map):
   #get a list of potential findings to replace. These are the ones from the negfinding map
    presence_map = isfinding_present(negfinding_map.keys(),orig_sentences)
    found=False
    rand_sentence = None
    matchingsentence = None
    i=0
    findinglist=list(presence_map.keys())
   # affectedfinding=[]
    while (not found) and (i<len(presence_map)):
        #picks a random finding
        matchedfinding=pick_finding(findinglist)
        matchingsentence = presence_map[matchedfinding]
        #affectedfinding.append(matchedfinding)
        if ((matchedfinding in negfinding_map) and (matchingsentence in negfinding_map[matchedfinding]) and (matchedfinding in posfinding_map)):
        #pick a random sentence from a pos_finding map
            rand_sentence = pick_random_sentence([matchingsentence], list(posfinding_map[matchedfinding]))
            #print("Converting negative finding to positive",
          #    matchedfinding,"->",matchingsentence,"->",rand_sentence)
            found=True
            #finding selected is matchedfinding, swap pairs are matchingsentence and rand sentence
        elif ((matchedfinding in posfinding_map) and (matchingsentence in posfinding_map[matchedfinding]) and (matchedfinding in negfinding_map)):
            rand_sentence = pick_random_sentence([matchingsentence], list(negfinding_map[matchedfinding]))
           # print("Converting positive finding to negative",
            #      matchedfinding,"->",matchingsentence,"->",rand_sentence)
            found=True

        if not found:
            i+=1
            
    if not found:
       # print("No replacement")
        return orig_sentences,process_count,real_sentenceMap,fake_sentencemap,None,None,[]
    
    else:
        finding_index = orig_sentences.index(matchingsentence)
        copy_sentences = orig_sentences.copy()
        deleted_sentence=copy_sentences[finding_index] 
        del copy_sentences[finding_index]
        copy_sentences.append(rand_sentence)
        fake_findingMap={}
        fake_findingMap[matchedfinding]=rand_sentence
        fake_sentencemap[filename]=fake_findingMap
        
        findingMap=report_to_finding_to_sentencesMap[filename]
        newfindingMap,affectedfinding=remove_sentence_with_finding(findingMap,deleted_sentence)
        real_sentenceMap[filename]=newfindingMap
        process_count+=1
        return copy_sentences,process_count,real_sentenceMap,fake_sentencemap,deleted_sentence,rand_sentence,affectedfinding
           
    
#main loop to go over the reports directory to produce a new report directory
#by various methods
def process_files(main_path, out_dir, findings,filename_map,problem_map,report_to_finding_to_sentencesMap,modification_method):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    count_process=0
    real_sentenceMap={}
    fake_sentenceMap={}
    modifsentenceMap={}
    deleted_sentenceMap={}
    added_sentenceMap={}
    affectedfindingMap={}
    for root, dirs, files in os.walk(main_path, topdown=False, onerror=None, followlinks=True):
        for filename in files:
            if filename != '.DS_Store':
                filepath = os.path.join(root, filename)
                orig_sentences = extract_sentences(filepath)
                modified_sentences,count_process,real_sentenceMap,fake_sentenceMap,deleted_sentence,added_sentence,affectedfindinglist = modification_method(orig_sentences,count_process,\
                                                                        report_to_finding_to_sentencesMap,real_sentenceMap,fake_sentenceMap,findings,\
                                                                       filename_map,filename,problem_map)
                
                modifsentenceMap[filename]= modified_sentences
                deleted_sentenceMap[filename] = deleted_sentence
                added_sentenceMap[filename] = added_sentence
                affectedfindingMap[filename]=affectedfindinglist
               # print(modification_method)
                #print(modified_sentences)
                #print(out_dir,filename)
                write_sentences(filename,out_dir,modified_sentences)
   # print("Files touched = ", count_process)
    
    return real_sentenceMap, fake_sentenceMap,modifsentenceMap,deleted_sentenceMap, added_sentenceMap,affectedfindingMap
    


    
    
    

    
