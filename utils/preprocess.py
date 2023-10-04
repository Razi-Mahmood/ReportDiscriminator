import numpy as np
import pandas as pd
import os
# extract the different problems from the dataset
def extract_findings(gtfile,chexpertlabelfile):
    reports = pd.read_csv(gtfile)
    problems = reports['Problems']
    problem_set = set()

    for row in problems:
        #if ('thorax' in row):
          #  print(row)
        problems = row.split(';')

        for problem in problems:
            cleanedproblem=problem.strip().lower()
            
           # if (cleanedproblem=='thorax'):
               # print("Row ", row,cleanedproblem)
            ##   print(problem)
            problem_set.add(cleanedproblem)
            
    chexreports = pd.read_csv(chexpertlabelfile,sep="\t")
    findings=chexreports['Findings']
    sentences=chexreports['sentence']
    sentenceFindingMap={}
    for i in range(len(chexreports.index)):
        finding=str(findings[i])
        sentence=str(sentences[i])
        sentence=sentence.replace("\"","")
        if sentence not in sentenceFindingMap:
            findingset=set()
        else:
            findingset=sentenceFindingMap[sentence]
        findingset.add(finding)
        sentenceFindingMap[sentence]=findingset
        
        
    
    return list(problem_set), sentenceFindingMap
def extract_findingsOld(gtfile):
    reports = pd.read_csv(gtfile)
    problems = reports['Problems']
    problem_set = set()

    for row in problems:
        #if ('thorax' in row):
          #  print(row)
        problems = row.split(';')

        for problem in problems:
            cleanedproblem=problem.strip().lower()
            
           # if (cleanedproblem=='thorax'):
               # print("Row ", row,cleanedproblem)
            ##   print(problem)
            problem_set.add(cleanedproblem)
    
    return list(problem_set)

def map_findings_to_sentences(orig_sentences,filename,findings,sentence_findingMap,problem_map,filename_map,report_to_finding_to_sentenceMap):
    #problem_map = this records the sentences that contain a finding key
    #filename_map= this records the findings in a report using report as the key
    #create an empty set dictionary for all problems
#     for p in findings:
#         problem_map[p] = set()
    findings_to_sentencesMap={}
    for sentence in orig_sentences:
        if sentence in sentence_findingMap:
            sentfindings=sentence_findingMap[sentence]
        else:
            sentfindings=None
        for keyword in problem_map:
            
            if (sentfindings is not None) and (keyword in sentfindings):
                if keyword not in findings_to_sentencesMap:
                    sentence_set=set()
                else:
                    sentence_set=findings_to_sentencesMap[keyword]
                sentence_set.add(sentence)
                findings_to_sentencesMap[keyword]=sentence_set
                problem_map[keyword].add(sentence)
                filename_map[filename].add(keyword)
            elif keyword in sentence:
                #print(keyword ,"->",sentence)
                    if keyword not in findings_to_sentencesMap:
                        sentence_set=set()
                    else:
                        sentence_set=findings_to_sentencesMap[keyword]
                        
                    sentence_set.add(sentence)
            
                    findings_to_sentencesMap[keyword]=sentence_set
                    problem_map[keyword].add(sentence)
                    filename_map[filename].add(keyword)
    report_to_finding_to_sentenceMap[filename]=findings_to_sentencesMap
 
    return problem_map,filename_map,report_to_finding_to_sentenceMap

def map_findings_to_sentencesOld(orig_sentences,filename,findings,problem_map,filename_map,report_to_finding_to_sentenceMap):
    #problem_map = this records the sentences that contain a finding key
    #filename_map= this records the findings in a report using report as the key
    #create an empty set dictionary for all problems
#     for p in findings:
#         problem_map[p] = set()
    findings_to_sentencesMap={}
    for sentence in orig_sentences:
        for keyword in problem_map:
            if keyword in sentence:
                #print(keyword ,"->",sentence)
                if keyword not in findings_to_sentencesMap:
                    sentence_set=set()
                else:
                    sentence_set=findings_to_sentencesMap[keyword]
                sentence_set.add(sentence)
                findings_to_sentencesMap[keyword]=sentence_set
                problem_map[keyword].add(sentence)
                filename_map[filename].add(keyword)
    report_to_finding_to_sentenceMap[filename]=findings_to_sentencesMap
 
    return problem_map,filename_map,report_to_finding_to_sentenceMap

# map problem finding --> corresponding sentences
def map_findings_to_sentencesOld(orig_sentences,filename,findings,problem_map,filename_map):
    #problem_map = this records the sentences that contain a finding key
    #filename_map= this records the findings in a report using report as the key
    #create an empty set dictionary for all problems
#     for p in findings:
#         problem_map[p] = set()
    for sentence in orig_sentences:
        for keyword in problem_map:
            if keyword in sentence:
                #print(keyword ,"->",sentence)
                problem_map[keyword].add(sentence)
                filename_map[filename].add(keyword)

                # for each sentence check if a keyword is in it
                    # if yes, add the sentence to the key value sets
   # for problem in problem_map:
    #    if (len(problem_map[problem])>0):
    #        print(problem ,"->",problem_map[problem])
            
    return problem_map,filename_map

def map_positive_negative_findings_to_sentences(orig_sentences,filename,findings,problem_map,filename_map):
    #problem_map = this records the sentences that contain a finding key
    #filename_map= this records the findings in a report using report as the key
    #create an empty set dictionary for all problems
#     for p in findings:
#         problem_map[p] = set()
    for sentence in orig_sentences:
        for keyword in problem_map:
            if keyword in sentence:
                #print(keyword ,"->",sentence)
                #check if this keyword matches a negative finding in that sentence
                problem_map[keyword].add(sentence)
                filename_map[filename].add(keyword)

                # for each sentence check if a keyword is in it
                    # if yes, add the sentence to the key value sets
   # for problem in problem_map:
    #    if (len(problem_map[problem])>0):
    #        print(problem ,"->",problem_map[problem])
            
    return problem_map,filename_map

def process_mapping(main_path, findings,sentence_findingMap):
    problem_map = {}
    filename_map={}
    origsentenceMap={}
    report_to_finding_to_sentenceMap={}
    for p in findings:
        problem_map[p] = set()
        # create empty set of problems
    
    for root, dirs, files in os.walk(main_path, topdown=False, onerror=None, followlinks=True):
        for filename in files:
            if filename != '.DS_Store':
                filepath = os.path.join(root, filename)
                orig_sentences = extract_sentences(filepath)
                origsentenceMap[filename]=orig_sentences
                filename_map[filename]=set() 
                
                 # creates maps from findings to sentences, and filenames to findings
                problem_map, filename_map,report_to_finding_to_sentenceMap = map_findings_to_sentences(orig_sentences,filename,
                                                                      findings,sentence_findingMap,problem_map,filename_map,report_to_finding_to_sentenceMap)
               
    return problem_map,filename_map,report_to_finding_to_sentenceMap,origsentenceMap
   

def process_mappingOld(main_path, findings):
    problem_map = {}
    filename_map={}
    for p in findings:
        problem_map[p] = set()
        # create empty set of problems
    
    for root, dirs, files in os.walk(main_path, topdown=False, onerror=None, followlinks=True):
        for filename in files:
            if filename != '.DS_Store':
                filepath = os.path.join(root, filename)
                orig_sentences = extract_sentences(filepath)
                filename_map[filename]=set() 
                
                 # creates maps from findings to sentences, and filenames to findings
                problem_map, filename_map = map_findings_to_sentences(orig_sentences,filename,
                                                                      findings,problem_map,filename_map)
               
    return problem_map,filename_map
                
def print_k_lines(hmap,k):
    i=0
    for key in hmap:
        if (i<k):
            print(i,key,hmap[key])
        i+=1
def print_k_set(hset,k):
    i=0
    for key in hset:
        if (i<k):
            print(i,key)
        i+=1
def extract_sentences(filepath):
    #print(filepath)
    file = open(filepath)
    allsent=[]
    for line in file:
        line1 = line.strip()
        sentences = line1.split('.') #separate the sentences
        i=0
        for sent in sentences:
            if len(sent) > 0:
                #print(i, sent.strip() + '.')
                allsent.append(sent.strip() + '.')
            i+=1
    file.close()
    return allsent

def write_sentences(filename,out_dir,modified_sentences):
    out_file_path = os.path.join(out_dir, filename)
    f = open(out_file_path, "w")
    for line in modified_sentences:
        f.write(line+"\n")
    f.close()
    
    
    
def capitalize_sentences(orig_sentences):
    if (type(orig_sentences) is list) or (type(orig_sentences) is set):
        revised_sentences = []
        for sent in orig_sentences:
            sent = sent.capitalize()            
            revised_sentences.append(sent)
        return revised_sentences
    else:
       # print(type(orig_sentences))
        return orig_sentences.capitalize() 
    

def capitalize_entries(origsentenceMap):
    #check if it is single indexed or double indexed hashmap
    # if single index is the value an array/list or direct value
    if origsentenceMap is None:
        return None
    
    revised_sentenceMap = {}
    
    for file in origsentenceMap:
        #revised_sentenceMap[file] = []
        
        content = origsentenceMap[file]
        if content is None:
            revised_sentenceMap[file]=None
            
        else:
            #content is either a list, a direct value or a hashmap
            if isinstance(content, dict):
                #handle dictionary case
                #print("Is a dictionary case")
                newcontent={}
                for finding in content:
                    #revised_sentenceMap[file] = []
                    
                    content_sentence_list = content[finding]
                    #print(content_sentence_list)
                    newcontent[finding] = capitalize_sentences(content_sentence_list)
                    
                revised_sentenceMap[file]=newcontent
                
            elif type(content) is list:
                #handle the list case          
                revised_sentenceMap[file] = capitalize_sentences(content)
                
            else:
               # print(type(content))
                #assume it is a direct value
                revised_sentenceMap[file]=content.capitalize()   
           
    return revised_sentenceMap

#code to parse the dicom file as a preparatory step to produce the labeled dataset for fake/real classification
def process_dicomfilenames(dicomdir):
    files_per_patient={}
    report_per_patient={}
    for root, dirs, files in os.walk(dicomdir, topdown=False, onerror=None, followlinks=True):
        for filename in files:
            if filename != '.DS_Store':
                filepath = os.path.join(root, filename)
               # print(filepath)
                filenametokens=filename.split("-")
                #6_IM-2192-1001 -> Here 6 is the report ID, 2192 is the patient id, 1001 is the study ID
                #usually 1001 is referring to first study which is frontal view, and 2001 is the side view
                patientid=filenametokens[1]
                reportname=filenametokens[0].split("_IM")[0] + ".txt"
                
                if 'CXR' not in reportname:
                    reportname = 'CXR' + reportname
                #print("Changed reportname = ",reportname)
                if patientid not in files_per_patient:
                    report_perdicom={}
                else:
                    report_perdicom=files_per_patient[patientid]
                if reportname not in report_perdicom:
                    dicom_array=[]

                else:
                    dicom_array=report_perdicom[reportname]
                dicom_array.append(filename)
                report_perdicom[reportname]=dicom_array
                files_per_patient[patientid]=report_perdicom
    sorted_files_per_patient={}
    for patientid in files_per_patient:
        report_perdicom=files_per_patient[patientid]
        sorted_perdicom={}
        for report in report_perdicom:
            dicom_array=report_perdicom[report]
            dicom_array=sorted(dicom_array)
           # print("Dicom sorted ",dicom_array)
            sorted_perdicom[report]=dicom_array
        sorted_files_per_patient[patientid]=sorted_perdicom
            
    return sorted_files_per_patient
    
                
                
                
         


    