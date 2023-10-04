import numpy as np
def binary_prscore(yarray_test,y_pred):
    p=0
    tp=0
    n=0
    tn=0
    fp=0
    fn=0
    for i in range(len(yarray_test)):
       if (yarray_test[i]==1):
           p+=1
           if (y_pred[i]==1):
               tp+=1
           else:
               fn+=1
       else:
           n+=1
           if (y_pred[i]==1):
               fp+=1
           else:
               tn+=1
    print (p,n,tp,fn,fp,tn)
    precision=tp/(tp+fp)
    recall=tp/p
    f1=(2*tp)/((2*tp)+fp+fn)
    accuracy=(tp+tn)/(p+n)
    print (precision,recall,f1,accuracy)
    return precision,recall,f1,accuracy

def record_per_findingcase(ml_df, recordedpairs_test, yarray_test, ypred):
    perturbMap={}
    tpMap={}
    for i in range(len(recordedpairs_test)):
        index=recordedpairs_test[i]
        method=ml_df.loc[index, "Method"]
        if method not in perturbMap:
            perturbMap[method]=1
        else:
            perturbMap[method]+=1
        if (yarray_test[i]==ypred[i]) :
            if method not in tpMap:
                tpMap[method]=1
            else:
                tpMap[method]+=1
    print(len(recordedpairs_test))
    total=0
    for method in perturbMap:
        total+=perturbMap[method]
        print(method,perturbMap[method],tpMap[method],perturbMap[method]/len(recordedpairs_test ))
        recall=tpMap[method]/perturbMap[method]
        print(method,recall)
    print(total)

def compute_roc_manual(y_pred,yarray_test,quant):
    p=0
    n=0
    for i in range(len(yarray_test)):
        if (yarray_test[i]==1):
            p+=1
        else:
            n+=1
    tprarray=[]
    fprarray=[]
    for threshrange in range(0,quant+1,1):
        thresh=(threshrange/quant)
        print(thresh)
        tp=0
        tn=0
        fp=0
        fn=0
        for i in range(len(y_pred)):
            if (y_pred[i,1]>thresh):
                ydecid=1
            else:
                ydecid=0
           # print(y_pred[i,1],, yarray_test[i])
            if (ydecid==yarray_test[i]):
                if (ydecid==1):
                    tp+=1
                else:
                    tn+=1
            else:
                if (ydecid==1):
                    fp+=1
                else:
                    fn+=1
                    
        tpr=tp/(tp+fn)
        fpr=fp/(fp+tn)
        tprarray.append(tpr)
        fprarray.append(fpr)
    auc = -1 * np.trapz(tprarray, fprarray)    
    
    return tprarray,fprarray,auc
def record_per_findingcaseincorrect(ml_df, recordedpairs_test, yarray_test, y_pred):
    perfindingMap={}
    precisionMap={} #tp/tp+fp
    recallMap={} #tp/p
    accuracyMap={}
    f1Map={}
    tpMap={}
    fpMap={}
    tnMap={}
    fnMap={}
    pMap={}
    nMap={}
    methodset=set()
    for i in range(len(yarray_test)):
        mlrowid=recordedpairs_test[i]
        method=ml_df.loc[mlrowid, "Method"]
        if (method=="Remove Random Finding") or (method=="Original"):
            correctlabel=1
        else:
            correctlabel=0
        if (yarray_test[i]==correctlabel):
            if method not in pMap:
                pMap[method]=1
            else:
                pMap[method]+=1
        else:
            if method not in nMap:
                 nMap[method]=1
            else:
                nMap[method]+=1
        if (yarray_test[i]==y_pred[i]):
            if (yarray_test[i]==1):
                #case of tp
                print(method)
                if method not in tpMap:
                    tpMap[method]=1
                else:
                    tpMap[method]+=1
            elif (yarray_test[i]==0):
                
                #case of tn
                if method not in tnMap:
                    tnMap[method]=1
                else:
                    tnMap[method]+=1
        elif (yarray_test[i]==1):
            #a case of false negative
            if method not in fnMap:
                fnMap[method]=1
            else:
                fnMap[method]+=1
        else:
            #case of fp
            if method not in fpMap:
                fpMap[method]=1
            else:
                fpMap[method]+=1
        methodset.add(method)
    for method in methodset:
        precisionMap[method]=tpMap[method]/(tpMap[method]+fpMap[method])
        recallMap[method]=tpMap[method]/pMap[method]
        accuracyMap[method]=(tpMap[method]+tnMap[method])/(pMap[method]+nMap[method])
        f1Map[method]=(2*tpMap[method])/((2*tpMap[method])+fpMap[method]+fnMap[method])
        print("Method ",method)
        print(method,precisionMap[method],recallMap[method],f1Map[method],accuracyMap[method])
    return precisionMap,recallMap,f1Map,accuracyMap