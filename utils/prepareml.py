import pandas as pd
import os

import sklearn

import numpy as np
from sklearn import metrics

import PIL
from PIL import ImageOps


from sklearn.metrics.pairwise import cosine_similarity


from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from sentence_transformers import SentenceTransformer, util
from PIL import Image
import numpy as np
from sklearn.datasets import make_classification
from sklearn.metrics import RocCurveDisplay
from sklearn.svm import SVC
import matplotlib.pyplot as plt
#creates a feature vector of number of images x image_size
def divide_patients(patientset,percentrain,percentest,percentdeploy):
    total = len(patientset)
    numtrain = int(percentrain*total)
    numtest = int(percentest*total)
    numdeploy = int(percentdeploy*total)
    print(total,numtrain,numtest,numdeploy)

def load_split(trainfile):
    file = open(trainfile, 'r')
    Lines = file.readlines()
    trainlist=[]
    for line1 in Lines:
        line=line1.split("\n")[0]
        trainlist.append(line)
    return trainlist
#load pre-divided splits
def load_splits(trainfile,testfile,deployfile):
    trainlist=load_split(trainfile)
    testlist=load_split(testfile)
    deploylist=load_split(deployfile)
    return trainlist,testlist,deploylist
    
def assemble_patientid(ml_df):
    distinctpatients=set()
    for i in range(len(ml_df.index)):
        patientid=str(ml_df.loc[i,"Patient ID"])
        distinctpatients.add(patientid)
    return distinctpatients
def assemble_images_reports(ml_df):
    distinctimages=set()
    distinctimageMap={}
    reportImageMap={}
    for i in range(len(ml_df.index)):
        images = ((ml_df.loc[i, "Images"].replace("['", '')).replace("']", '').replace("'", '').replace(" ", "")).split(',')
        tgtimage=images[0]
        patientid=str(ml_df.loc[i,"Patient ID"])
        reportname=str(ml_df.loc[i,"Report Name"])
        distinctimages.add(tgtimage)
        distinctimageMap[tgtimage]=patientid
        reportImageMap[reportname]=tgtimage
            
        
    print("Number of unique images=",len(distinctimages))
    return distinctimages,distinctimageMap,reportImageMap

def assemble_sentences(ml_df):
    distinct_sents=set()
    for i in range(len(ml_df.index)):
        sentence = ml_df.loc[i, "sentence"]
        distinct_sents.add(sentence)
    print("Number of unique sentences=",len(distinct_sents))
    return distinct_sents


def create_image_arrays(distinctimages,img_dir):
    #imgarray=np.array(len(distinxctimages),(224,224,1))
    imgarray=np.zeros((len(distinctimages), 224, 224, 3))
    i = 0
    
    for distinctimage in distinctimages:
        print(distinctimage)
    
        imagepath = img_dir + distinctimage
        img = image.load_img(imagepath, target_size=(224, 224))
        
        #img = PIL.ImageOps.grayscale(img)
        x = image.img_to_array(img)

        print(x.shape)
        imgarray[i] = x
        
        i+=1
    
    return imgarray

def print_k_map(hmap,k):
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

def create_image_arraysclip_filter(filterpatients,distinctimageMap,img_dir,model):
    imgarray=[]
    imgnames=[]
    imgindex={}
   # i=0
    k=0
    for distinctimage in distinctimageMap:
        
       # if (i<10):
      #  if (i%100==0):
        #    print(i,"out of ",len(distinctimageMap))
        patientid=distinctimageMap[distinctimage]
        #checks to see if the image belongs to the patient in the desired set (train, test, deploy)
        if (patientid in filterpatients):
            imagepath = img_dir + distinctimage
            img=Image.open(imagepath)
            #img = image.load_img(imagepath, target_size=(224, 224))
            imgarray.append(img)
            imgnames.append(distinctimage)
            imgindex[distinctimage]=k
            k+=1
       # i+=1

    print(len(imgarray))
    img_vec = model.encode(imgarray)

    return imgindex,imgnames,img_vec #vector form


#creates image arrays     
def create_image_arraysclip(distinctimages,img_dir,model):
    imgarray=[]
    imgnames=[]
    imgindex={}
    i=0
    for distinctimage in distinctimages:
       # if (i<10):
        if (i%100==0):
            print(i,"out of ",len(distinctimages))
        imagepath = img_dir + distinctimage
        img=Image.open(imagepath)
        #img = image.load_img(imagepath, target_size=(224, 224))
        imgarray.append(img)
        imgnames.append(distinctimage)
        imgindex[distinctimage]=i
        i+=1

    print(len(imgarray))
    img_vec = model.encode(imgarray)

    return imgindex,imgnames,img_vec #vector form

#creates feature vector for image array
def encode_images(imgarray):
    img_features = base_model.predict(imgarray)
    imgfeat=img_features.reshape(len(imgarray),7*7*512)
    return imgfeat



def encode_cliptext(distinct_text,model):
    textnames=[]
    textindex={}
    i=0
    for text in distinct_text:
        if (i%100==0):
            print(i,text)
        textnames.append(text)
        textindex[text]=i
        i+=1
        
    text_vec = model.encode(textnames)
    
    return textindex,textnames,text_vec

def encode_text(distinct_text,bertmodel):
    textarray=[]
    textMap={}
    for text in distinct_text:
        textarray.append(text)
        
    feature_vector = bertmodel.encode(textarray)
    for i in range(len(textarray)):
        textMap[textarray[i]]=feature_vector[i]
    return textarray,textMap

#textindex maps a sentence to its indx, imgindex maps an image to its index
def form_combined_feature_vector(ml_df,textindex,imgindex,text_vec,image_vec):
    #xarray=np.zeros((len(ml_df.index), 7*7*512+384))
   # xarray=np.zeros((len(ml_df.index), 1024)
   # yarray=np.zeros((len(ml_df.index)))
    xarray=[]
    yarray=[]
    uniquesent=set()
    findingset=set()
    reportset=set()
    reportfakeset=set()
    reportrealset=set()
    recordedpairs=[]
    mlrowid=0
    #going over the rows of the ml_df dataframe which list images and their sentences paired some of which are fake and some real
    for i in range(len(ml_df.index)):
        mlrowid=i
        if (i%100==0):
            print(i, " out of ",len(ml_df.index))
        images = ((ml_df.loc[i, "Images"].replace("['", '')).replace("']", '').replace("'", '').replace(" ", "")).split(',')
        tgtimage=images[0]
        sentence = ml_df.loc[i, "sentence"]
        label=ml_df.loc[i, "Real/Fake"]
        finding=ml_df.loc[i, "Findings Present/Absent"]
        reportname=ml_df.loc[i, "Report Name"]
        #checking the tgtimage (it is a string) is in the list of images in the train/test partition
        #the imgindex is already filtered to the list of images in the train/test partition, hence checking for the presence of this in the map is sufficient
        if (sentence in textindex) and (tgtimage in imgindex):
           # print(reportname)
            recordedpairs.append(mlrowid)
           # recordedpairs.append(reportname+"\t"+sentence)
            ti=textindex[sentence]
            ii=imgindex[tgtimage]
            tvec=text_vec[ti]
            ivec=image_vec[ii]
            uniquesent.add(sentence)
            key=reportname +"\t"+label
            if (label=="Real"):
                keyreal=reportname +"\t"+label
                reportrealset.add(key)
            else:
                keyfake=reportname +"\t"+label
                reportfakeset.add(key)
            combvec=np.concatenate((ivec,tvec),axis=0)
           # xarray[i]=combvec
            #yarray[i]=label
            xarray.append(combvec)
            
            if (label=='Real'):
                yarray.append(1)
            else:
                yarray.append(0)
            #yarray.append(label)
            findingset.add(finding)
            reportset.add(reportname)
           
    print (len(findingset),len(uniquesent),len(reportset),len (reportfakeset),len(reportrealset), " unique")

    return xarray,yarray,recordedpairs # returns the image-text pair, labels
#get cosine similarity values directly between the vectors
def form_sep_vectors(ml_df,textindex,imgindex,text_vec,image_vec):
    #xarray=np.zeros((len(ml_df.index), 7*7*512+384))
   # xarray=np.zeros((len(ml_df.index), 1024)
   # yarray=np.zeros((len(ml_df.index)))
    xarray=[]
    yarray=[]
    xsimple=[]
    uniquesent=set()
    findingset=set()
    reportset=set()
    reportfakeset=set()
    reportrealset=set()
    recordedpairs=[]
    mlrowid=0
    #going over the rows of the ml_df dataframe which list images and their sentences paired some of which are fake and some real
    for i in range(len(ml_df.index)):
        mlrowid=i
        if (i%100==0):
            print(i, " out of ",len(ml_df.index))
        images = ((ml_df.loc[i, "Images"].replace("['", '')).replace("']", '').replace("'", '').replace(" ", "")).split(',')
        tgtimage=images[0]
        sentence = ml_df.loc[i, "sentence"]
        label=ml_df.loc[i, "Real/Fake"]
        finding=ml_df.loc[i, "Findings Present/Absent"]
        reportname=ml_df.loc[i, "Report Name"]
        #checking the tgtimage (it is a string) is in the list of images in the train/test partition
        #the imgindex is already filtered to the list of images in the train/test partition, hence checking for the presence of this in the map is sufficient
        if (sentence in textindex) and (tgtimage in imgindex):
           # print(reportname)
            recordedpairs.append(mlrowid)
           # recordedpairs.append(reportname+"\t"+sentence)
            ti=textindex[sentence]
            ii=imgindex[tgtimage]
            tvec=text_vec[ti]
            ivec=image_vec[ii]
            uniquesent.add(sentence)
            key=reportname +"\t"+label
            if (label=="Real"):
                keyreal=reportname +"\t"+label
                reportrealset.add(key)
            else:
                keyfake=reportname +"\t"+label
                reportfakeset.add(key)
            #record cosine similarity here
            D12=cosine_similarity([ivec,tvec])
            #print(ivec.shape)
            score=D12[0,1]
            xsimple.append(np.array([score]))
           
            combvec=np.concatenate((ivec,tvec),axis=0)
           # xarray[i]=combvec
            #yarray[i]=label
            xarray.append(combvec)
            
            if (label=='Real'):
                yarray.append(1)
            else:
                yarray.append(0)
            #print(score,label)
            #yarray.append(label)
            findingset.add(finding)
            reportset.add(reportname)
           
    print (len(findingset),len(uniquesent),len(reportset),len (reportfakeset),len(reportrealset), " unique")

    return xarray,yarray,xsimple,recordedpairs # returns the image-text pair, labels
                                
def get_correspondingimage_rep(ml_df):
    rep_to_imgMap={}
    for i in range(len(ml_df.index)):
        if (i%100==0):
            print(i, " out of ",len(ml_df.index))
        images = ((ml_df.loc[i, "Images"].replace("['", '')).replace("']", '').replace("'", '').replace(" ", "")).split(',')
        tgtimage=images[0]
        reportname=ml_df.loc[i, "Report Name"]
        rep_to_imgMap[reportname]=tgtimage
    return rep_to_imgMap