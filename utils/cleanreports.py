import os
import PIL
from PIL import ImageOps
from PIL import Image
import numpy as np
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
    
#collect all sentences and all image names across reports for vectorization and feature formation                        
def collect_allunique_items(topaidir,img_dir,model,reportImageMap ):
    imagenamesset=set()
    sentenceset=set()
    for root, dirs, files in os.walk(topaidir, topdown=False, onerror=None, followlinks=True):
        for filename in files:
            if filename != '.DS_Store':
                filepath = os.path.join(root, filename)
                allsents=extract_sentences(filepath)
                reportname=filename.split("_")[0]
                imagename=reportImageMap[reportname]
                imagenamesset.add(imagename)
                for sent in allsents:
                    sentenceset.add(sent)
    sentencelist=list(sentenceset)
    imagenameslist=list(imagenamesset)
    sentindex={}
    for i in range(len(sentencelist)):
        sentindex[sentencelist[i]]=i
    imgindex={}
    imgarray=[]
    for i in range(len(imagenameslist)):
        distinctimage = imagenameslist[i]
        imagepath = img_dir + distinctimage
        img=Image.open(imagepath)
            #img = image.load_img(imagepath, target_size=(224, 224))
        imgarray.append(img)
        imgindex[distinctimage]=i
    img_vec = model.encode(imgarray)
    text_vec = model.encode(sentencelist)
    return sentencelist,imagenameslist,sentindex,imgindex,text_vec,img_vec

def classify_report_sentences(clfmodel,topaidir,topmodifdir,img_vec,text_vec,sentindex,imgindex,sentencelist,imagenameslist,reportImageMap):
    xarray=[]
    imagereplist=[]
    elim=0
    countreal=0
    countfake=0
    count=0
    countreduceMap={}
    if not os.path.exists(topmodifdir):
       os.makedirs(topmodifdir)
    for root, dirs, files in os.walk(topaidir, topdown=False, onerror=None, followlinks=True):
        for filename in files:
            if filename != '.DS_Store':
                filepath = os.path.join(root, filename)
                modifpath=topmodifdir+"/"+filename
                print(filepath,modifpath)
                count+=1
                reportname=filename.split("_")[0]
                imagename=reportImageMap[reportname]
                allsents=extract_sentences(filepath)
                reportname=filename.split("_")[0]
                imagename=reportImageMap[reportname]
                xarray=[]
                recordedpair=[]
                for sent in allsents:
                    sentid=sentindex[sent]
                    imgid=imgindex[imagename]
                    ivec=img_vec[imgid]
                    tvec=text_vec[sentid]
                    combvec=np.concatenate((ivec,tvec),axis=0)
                    xarray.append(combvec)
                    recordedpair.append(sent+"\t"+imagename)
                #now classify this array
                ypred=clfmodel.predict(xarray)
                revisedreport=[]
                for i in range(len(ypred)):
                    if (ypred[i]==1):
                        countreal+=1
                        sent=recordedpair[i].split("\t")[0]
                        revisedreport.append(sent)
                    else:
                        countfake+=1
                print(len(revisedreport), len(allsents))
                diff=len(allsents)-len(revisedreport)
                if diff not in countreduceMap:
                    countreduceMap[diff]=1
                else:
                    countreduceMap[diff]+=1
                if (len(revisedreport)==0):
                    print(revisedreport,recordedpair)
                    elim+=1
                else:
                    f=open(modifpath,"w")
                    for sent in revisedreport:
                        f.write(sent+"\n")
                    f.close()
    print("Number of empty modified reports = ", elim,countreal,countfake,count)
    return countreduceMap
                   
#takes the sentences in the aiMap and recovers the sentence and reportid, and indexes to get the prediction
def modify_reports_old(recordedpairs_deploy,y_pred_deploy,y_array_deploy,origMap,aiMap):
    modifMap={}
    notindeploy=0
    ntotal=0
    indexset=set()
    for key in aiMap:
        aireport=aiMap[key]
        #print(key,aireport,len(aireport))
        
        modifreport=""
        sentarray=aireport.split(".")
       # print(sentarray)
        for sent in sentarray:
            if (len(sent)>0):
                ntotal+=1
                origsent=sent+"."
                newsent=origsent.lower()
                keysplit=key.split("\t")
               # newkey="CXR"+keysplit[0]+".txt"+"\t"+newsent
                newkey=keysplit[0]+"\t"+newsent
                #print(key,newkey,newsent)
                #print("Matching " ,newkey)
                if (newkey in recordedpairs_deploy):
                    #i.e part of deploy patient set
                    
                    index=recordedpairs_deploy.index(newkey)
                    indexset.add(index)
                    predictedlabel=y_pred_deploy[index]
                    if (predictedlabel=='Real'):
                        modifreport+=origsent
                    else:
                       # print("Match found ",newkey)
                       # print(index)
                        if (predictedlabel==y_array_deploy[index]):
                            print("Dropping ", newkey)
                else:
                    #print(newkey, " not in deploy")
                    modifreport+=origsent #should do a fresh classify here 
                    notindeploy+=1
        if key not in modifMap:
            modifMap[key]=modifreport
    print( notindeploy,ntotal)
    return modifMap,indexset   
    
#takes the AI-generated reports and modifies them based on the classifier model 
#collect all image-sentence pairs across all ai reports and encode them
#then send to classifier to get their labels
def create_modified_reports(clfmodel,model,topaidir,img_dir,topmodifdir,reportImageMap):
    #recover the sentence and image associated with this report
    sentencelist,imagenameslist,sentindex,imgindex,text_vec,img_vec=collect_allunique_items(topaidir,img_dir,model,reportImageMap)
    count_reduceMap=classify_report_sentences(clfmodel,topaidir,topmodifdir,img_vec,text_vec,sentindex,imgindex,sentencelist,imagenameslist,reportImageMap)
    return sentencelist,imagenameslist,sentindex,imgindex,text_vec,img_vec,count_reduceMap