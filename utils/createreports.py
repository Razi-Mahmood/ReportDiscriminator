
#create the fake/real dataset for training a classifier

# Patient ID \t Report Name\t Images\t Actual Report\t Findings present\t Modified report \t 
# findings touched \t sentence added\t Sentence Removed
         

#'patientid', 'filename', 'dicom_files', 'findings', 'sentence', 'real/fake'

#1. Loop over patient id
#for each patient pid:
#.  Retrieve the report name, add to the report name column
#.  Retrieve the dicom files, add to the dicom files column (all dicom files in a single cell , comma separated)
#. Go over the real_finding_map per report
# for each finding in real_finding_map per report:
# create a row by listing the patientid, reportname, dicom files,findingname, and the sentence associated with the fidning in that report
#IN the fake/real label column, add the label "Real"

# Repeat the above procedure for fake_finding_map
# Add label ='Fake in the label column

import numpy as np
import pandas as pd
import os


from utils.fakereporting import *
from sklearn import svm
from sklearn.model_selection import train_test_split

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
    


def create_label_row(sorted_files_per_patient, real_sentenceMap, fake_sentenceMap,rows):
    
    count=0
    for pid in sorted_files_per_patient:
      #  print(pid)
        
        report_filenames = sorted_files_per_patient[pid]
        for report in report_filenames:
           # print(report)
            dicom_files = report_filenames[report]
            if report in real_sentenceMap:
                real_sentences_perfinding=real_sentenceMap[report]
                for finding in real_sentences_perfinding:

                  #  print(finding)
                    sentences=real_sentences_perfinding[finding]

                    if (type(sentences) is set):
                        for sent in sentences:

                    #for sentence in actual_sentences:  
                            new_row={}
                            new_row['Patient ID']=pid
                            new_row['Report Name']=report
                            new_row['Images']= dicom_files
                            new_row['Findings Present'] = finding
                            new_row['sentence'] = sent
                            new_row['Real/Fake'] = 'Real'
                            new_row=pid+"\t"+report+"\t"+str(dicom_files)+"\t"+finding+"\t"+sent+"\tReal"
                            rows.add(new_row)
                            #rows.append(new_row)
                            count+=1
                    else:
                        new_row={}
                        new_row['Patient ID']=pid
                        new_row['Report Name']=report
                        new_row['Images']= dicom_files
                        new_row['Findings Present'] = finding
                        new_row['sentence'] = sentences
                        new_row['Real/Fake'] = 'Real'
                        new_row=pid+"\t"+report+"\t"+str(dicom_files)+"\t"+finding+"\t"+sentences+"\tReal"
                        rows.add(new_row)
                        count+=1
        
        #might want to create a new hashmap??
            if report in fake_sentenceMap:
                fake_sentences_perfinding=fake_sentenceMap[report]
                for finding in fake_sentences_perfinding:
                    sentences=fake_sentences_perfinding[finding]

                    if (type(sentences) is set):
                        for sent in sentences:

                    #for sentence in actual_sentences:  
                            new_row={}
                            new_row['Patient ID']=pid
                            new_row['Report Name']=report
                            new_row['Images']= dicom_files
                            new_row['Findings Present'] = finding
                            new_row['sentence'] = sent
                            new_row['Real/Fake'] = 'Fake'
                            new_row=pid+"\t"+report+"\t"+str(dicom_files)+"\t"+finding+"\t"+sent+"\tFake"

                            rows.add(new_row)
                            count+=1
                    else:
                        new_row={}
                        new_row['Patient ID']=pid
                        new_row['Report Name']=report
                        new_row['Images']= dicom_files
                        new_row['Findings Present'] = finding
                        new_row['sentence'] = sentences
                        new_row['Real/Fake'] = 'Fake' 
                        new_row=pid+"\t"+report+"\t"+str(dicom_files)+"\t"+finding+"\t"+sentences+"\tFake"
                        rows.add(new_row)
                        count+=1
        
    return rows         

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

        
   
#code to generate the report modification data for easy consumption by radiologists
#the excel spread sheet row will be of hte following format
#patientid \t reportname \t dicom files \t findings per report \t Original report \t Modified report \t Sentence deleted \t Sentence added
def create_report_row(sorted_files_per_patient, originalreportMap,modifiedreportMap, \
                        addedsentenceMap, deletedsentenceMap, method,affectedfindingMap,rows):
    
    count=0
    for pid in sorted_files_per_patient:
#        print(pid)
        
        report_filenames = sorted_files_per_patient[pid]
    #    print_k_lines(addedsentenceMap,3)
     #   print_k_lines(deletedsentenceMap,4)
        for report in report_filenames:
            if (report in addedsentenceMap) or (report in deletedsentenceMap):
           # if (addedsentenceMap[report] is not None) or (deletedsentenceMap[report] is not None):
       
            #print(report)
                dicom_files = report_filenames[report]

                original_report= originalreportMap[report]
                original_report_str = ' '.join(original_report)

                modified_report= modifiedreportMap[report]
                modified_report_str = ' '.join(modified_report)

                added_sentence= str(addedsentenceMap[report])
                #added_sentence_str = ''.join(added_sentence)

                deleted_sentence= str(deletedsentenceMap[report])
                #deleted_sentence_str = ''.join(deleted_sentence)
                affectedfinding=affectedfindingMap[report]
               # print(affectedfinding,method)

                new_row=pid+"\t"+report+"\t"+str(dicom_files)+"\t"+original_report_str+"\t"+modified_report_str+"\t"+added_sentence+"\t"+deleted_sentence+"\t"+str(affectedfinding)+"\t"+method
                #rows.append(new_row)
                rows.add(new_row) #takes care of repeats
            else:
                print("Skipping report ", report,len(addedsentenceMap),len(deletedsentenceMap))
         
            
    return rows



def create_report_row_withoutdicom( originalreportMap,modifiedreportMap, \
                        addedsentenceMap, deletedsentenceMap, method,affectedfindingMap,rows):
    
    count=0
    for report in originalreportMap:
        if (addedsentenceMap[report] is not None) or (deletedsentenceMap[report] is not None):
           
            original_report= originalreportMap[report]
            original_report_str = ' '.join(original_report)

            modified_report= modifiedreportMap[report]
            modified_report_str = ' '.join(modified_report)
            added_sentence= str(addedsentenceMap[report])
            #added_sentence_str = ''.join(added_sentence)

            deleted_sentence= str(deletedsentenceMap[report])
            #deleted_sentence_str = ''.join(deleted_sentence)
            affectedfinding=affectedfindingMap[report]
           # print(affectedfinding,method)

            new_row=report+"\t"+original_report_str+"\t"+modified_report_str+"\t"+added_sentence+"\t"+deleted_sentence+"\t"+str(affectedfinding)+"\t"+method
           # print(new_row)

            rows.add(new_row)

    return rows
def create_all_rows(indir,outdir, findings, neg_map,filename_map, problem_map, 
                                                  report_to_finding_to_sentenceMap,files_per_patient):
    rows=set()
  #  print("Remove random finding")
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"removerandom/", findings, filename_map, problem_map,report_to_finding_to_sentenceMap,remove_random_finding)
  #  print("Add random finding")
    rows = create_label_row(files_per_patient, real_sentenceMap, fake_sentenceMap,rows)
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"addrandom/", findings, filename_map, problem_map, 
                                                  report_to_finding_to_sentenceMap,add_random_finding)
    rows = create_label_row(files_per_patient, real_sentenceMap, fake_sentenceMap,rows)
   # print("Exchange finding")
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"exchange/", findings, filename_map, problem_map, 
                                                  report_to_finding_to_sentenceMap,exchange_finding)
    rows = create_label_row(files_per_patient, real_sentenceMap, fake_sentenceMap,rows)
  #  print("Reverse finding")
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"reversefinding/", neg_map, filename_map, problem_map, 
                                                     report_to_finding_to_sentenceMap,reverse_finding)
    rows = create_label_row(files_per_patient, real_sentenceMap, fake_sentenceMap,rows)
    return rows

def create_all_reportrows(indir,outdir, findings, files_per_patient,neg_map,filename_map, problem_map, 
                                                  report_to_finding_to_sentenceMap,revised_sentenceMap):
    rows=[]
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"removerandom/", findings, filename_map, problem_map, 
                                                      report_to_finding_to_sentenceMap,add_random_finding)
  #  print(len(deleted_sentenceMap),len(added_sentenceMap))
    rows=create_report_row(files_per_patient,revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap), "Add Random Finding",affectedfindingMap,rows)
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"addrandom/", findings, filename_map, problem_map, 
                                                      report_to_finding_to_sentenceMap,remove_random_finding)
    rows=create_report_row(files_per_patient,revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap),"Remove Random Finding",affectedfindingMap,rows)
    
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"exchange/", findings, filename_map, problem_map, 
                                                      report_to_finding_to_sentenceMap,exchange_finding)
    rows=create_report_row(files_per_patient,revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap), "Exchange Finding",affectedfindingMap,rows)
    
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"reversefinding/", neg_map, filename_map, problem_map, 
                                                     report_to_finding_to_sentenceMap,reverse_finding)
    rows=create_report_row(files_per_patient,revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap),"Reverse Finding",affectedfindingMap,rows)
   
    return rows

def create_all_reportrows_withoutdicom(indir,outdir, findings, neg_map,filename_map, problem_map, 
                                                  report_to_finding_to_sentenceMap,revised_sentenceMap,rows):
  
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"removerandom/", findings, filename_map, problem_map, 
                                                      report_to_finding_to_sentenceMap,add_random_finding)
    rows=create_report_row_withoutdicom(revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap), "Add Random Finding",affectedfindingMap,rows)
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"addrandom/", findings, filename_map, problem_map, 
                                                      report_to_finding_to_sentenceMap,remove_random_finding)
    rows=create_report_row_withoutdicom(revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap),"Remove Random Finding",affectedfindingMap,rows)
    
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"exchange/", findings, filename_map, problem_map, 
                                                      report_to_finding_to_sentenceMap,exchange_finding)
    rows=create_report_row_withoutdicom(revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap), "Exchange Finding",affectedfindingMap,rows)
    
    real_sentenceMap, fake_sentenceMap,modified_sentences,deleted_sentenceMap,added_sentenceMap,affectedfindingMap=process_files(indir,outdir+"reversefinding/", neg_map, filename_map, problem_map, 
                                                     report_to_finding_to_sentenceMap,reverse_finding)
    rows=create_report_row_withoutdicom(revised_sentenceMap, capitalize_entries(modified_sentences),
                        capitalize_entries(added_sentenceMap), capitalize_entries(deleted_sentenceMap),"Reverse Finding",affectedfindingMap,rows)
   
    return rows
def writerows(header,rows,outfilename):
    #outfilename=outdir+"/"+outfile
  #  print(outfilename)
    fout=open(outfilename,"w")
    fout.write(header+"\n")
    #fout.write("Patient ID\tReport Name\tImages\tFindings Present\tsentence\tReal/Fake\n")
    for row in rows:
        fout.write(row+"\n")
    fout.close()
#divide the dataset into train-test-correct/deploy splits
#move the reports belonging to the train-test splits away from the deploy split
#for the deploy split, create three folders, for original, ai-generated, and corrected to apply the report correction algorithm
#using the 60-20-20 based on patients
from sklearn import svm
from sklearn.model_selection import train_test_split
def prepare_splits(fakefilesrows,files_per_patient,outdir):
  #  df = pd.read_csv(fakedatasetfile, delimiter = "\t")
    df = pd.read_csv(fakefilesrows, delimiter = "\t")
    reportcol=df['Report Name']
    reportlist=[]
    reportToPatientMap={}
    for i in range(len(df.index)):
        reportlist.append(str(reportcol[i]))
   # print(len(reportlist))
    patientset=set()
    for patientid in files_per_patient:
        reportl=files_per_patient[patientid]
        for report in reportl:
            if (report in reportlist):     
                patientset.add(patientid)
                reportToPatientMap[report]=patientid
   # print("Recalculated  = ",len(patientset))
    patientlist=list(patientset)
        
    patients_train, patient_test1 = train_test_split(patientlist,  test_size=0.4, random_state=42) #this does the 60-40 split first
  #  print(len(patients_train),len(patient_test1))
    patients_test,patients_deploy = train_test_split(patient_test1,  test_size=0.5, random_state=12) #tis does the 50-50 of the 40 giving 20-20
    print(len(patients_train),len(patients_test),len(patients_deploy))
    f=open(outdir+"train.txt","w")
    for pid in patients_train:
        f.write(pid+"\n")
    f.close()
    f=open(outdir+"test.txt","w")
    for pid in patients_test:
        f.write(pid+"\n")
    f.close()
    f=open(outdir+"correct.txt","w")
    for pid in patients_deploy:
        f.write(pid+"\n")
    f.close()
    
    return patients_train,patients_test,patients_deploy,reportToPatientMap
    
#now deposit the real and AI reports in the deploy directory
def save_holdoutdata(fakefilesrows,reportToPatientMap,patients_deploy,outdir):
  #  df = pd.read_csv(fakedatasetfile, delimiter = "\t")
    df = pd.read_csv(fakefilesrows, delimiter = "\t")
    reportcol=df['Report Name']
    origreportcol=df['Original Report']
    modifreportcol=df['Modified Report']
    origpath=outdir+"/origreports/"
    aipath=outdir+"/aireports/"
    if not os.path.exists(origpath):
       os.makedirs(origpath)
    if not os.path.exists(aipath):
       os.makedirs(aipath)
    print("modif rows= ",len(modifreportcol),len(origreportcol))
    count=0
    reportMap={}
    
    for i in range(len(df.index)):
        
        reportname=str(reportcol[i])
        origreport=str(origreportcol[i])
      #  print(i,reportname)
        modifreport=str(modifreportcol[i])
        patientid=reportToPatientMap[reportname]
        if (patientid in patients_deploy):
        #    print(reportname,patientid)
            count+=1
            if (reportname not in reportMap):
                reportMap[reportname]=1
            else:
                reportMap[reportname]+=1
            fullpathorigreport=origpath+reportname+"_"+str(reportMap[reportname])
            fullpathaireport=aipath+reportname+"_"+str(reportMap[reportname])
            f1=open(fullpathorigreport,"w")
            f2=open(fullpathaireport,"w")
            f1.write(origreport+"\n")
            f2.write(modifreport+"\n")
            f1.close()
            f2.close()
            
    print(count)
def add_original_sentences(origreport,patientid,reportname,imagename,rowid,rowMap):
    origtokens=origreport.replace("\"","").split(".")
    for j in range(len(origtokens)):
        if (origtokens[j].strip()!=""):
            sent=origtokens[j]+"."
            sent=sent.lower()
            row=patientid+"\t"+reportname+"\t"+imagename[0]+"\t"+"Unknown"+"\t"+sent+"\tReal\t"+"Original"
           # print(row)
            if row not in rowMap:
                rowMap[row]=rowid
                rowid+=1  
    return rowid,rowMap
#place only the train and test patients in the ML_dataset.txt    
def create_ml_dataset(fakefilesrows,reportToPatientMap,patients_train,patients_test,patients_deploy,files_per_patient,outfile,includeOrig=False):
  #  df = pd.read_csv(fakedatasetfile, delimiter = "\t")
    df = pd.read_csv(fakefilesrows, delimiter = "\t")
    reportcol=df['Report Name']
    origreportcol=df['Original Report']
    modifreportcol=df['Modified Report']
    affected_findingcol=df['AffectedFinding']
    sentence_addedcol=df['Sentence Added']
    sentence_deletedcol=df['Sentence Deleted']
    methodcol=df['Method']
   # print("modif rows= ",len(modifreportcol),len(origreportcol))
    count=0
    rowMap={}
    rowid=0
    file1 = open(fakefilesrows, 'r')
    Lines = file1.readlines()
    rowcount=0
    for line1 in Lines:
        line=line1.split("\n")[0]
        if (rowcount>0):
            linetokens=line.split("\t")
            if (len(linetokens)==7):
               # print(line)
                """

                reportname=str(reportcol[i])
                origreport=str(origreportcol[i])
                modifreport=str(modifreportcol[i])
                affectedfinding=str(affected_findingcol[i])
                sentencea=str(sentence_addedcol)
                sentencer=str(sentence_deletedcol[i])
                method=str(methodcol[i])
                """
                reportname=linetokens[0]
                origreport=linetokens[1]
                modifreport=linetokens[2]
                sentencea=linetokens[3]
                sentencer=linetokens[4]
                affectedfinding=linetokens[5]
                method=linetokens[6]
                #print(reportname,origreport,modifreport,affectedfinding,sentencea,sentencer,method)
                patientid=reportToPatientMap[reportname]
                imagename=files_per_patient[patientid][reportname]
                if ((patientid in patients_train)or (patientid in patients_test) or (patientid in patients_deploy)):
                #    print("Matches train or test patient ", reportname,patientid)
                #    print(linetokens)
                    
                #all original report sentences get the label of real for their image
                    if includeOrig:
                        rowid,rowMap=add_original_sentences(origreport,patientid,reportname,imagename,rowid,rowMap)
                  
                   # count+=1
                    #print(i,count)
                    #prepare the following row
                    #Patient ID	Report Name	Images	Findings Present/Absent	sentence	Real/Fake
                    row=None
                    row1=None
                    row2=None
                    label=None
                 #   print("Method = ",method, 'Add Random Finding')
                    if (method=='Add Random Finding'):
                        sentence=sentencea.lower()
                        label="Fake"
                        row=patientid+"\t"+reportname+"\t"+imagename[0]+"\t"+affectedfinding
                        row+="\t"+sentence+"\t"+label+"\t"+"Add Random Finding"
                    elif (method=='Remove Random Finding'):
                        sentence=sentencer.lower()
                        label="Real"
                        row=patientid+"\t"+reportname+"\t"+imagename[0]+"\t"+affectedfinding
                        row+="\t"+sentence+"\t"+label+"\t"+"Remove Random Finding"
                    elif (method=='Exchange Finding') or (method=='Reverse Finding'):
                        sentencea=sentencea.lower()
                        labela="Fake"
                        sentencer=sentencer.lower()
                        labelr="Real"
                        midrow=patientid+"\t"+reportname+"\t"+imagename[0]+"\t"+affectedfinding
                        if (method=="Exchange Finding"):
                            row1=midrow+"\t"+sentencea+"\t"+labela+"\t"+"Exchange Finding"
                            row2=midrow+"\t"+sentencer+"\t"+labelr+"\t"+"Exchange Finding"
                        else:
                            row1=midrow+"\t"+sentencea+"\t"+labela+"\t"+"Reverse Finding"
                            row2=midrow+"\t"+sentencer+"\t"+labelr+"\t"+"Reverse Finding"

                    if ((row is not None) and (row not in rowMap)):
                        rowMap[row]=rowid
                        rowid+=1 
                    #    print(row)
                    if ((row1 is not None) and (row1 not in rowMap)):
                        rowMap[row1]=rowid
                        rowid+=1
                      #  print(row1)
                    if ((row2 is not None) and (row2 not in rowMap)):
                        rowMap[row2]=rowid
                        rowid+=1 
                      #  print(row2)
                
        rowcount+=1
   # print(len(rowMap),rowid)        
    #print(count)
    f=open(outfile,"w")
    f.write("Patient ID\tReport Name\tImages\tFindings Present/Absent\tsentence\tReal/Fake\tMethod\n")
    for row in rowMap:
        f.write(row+"\n")
    f.close()
    
    return rowMap
    
 