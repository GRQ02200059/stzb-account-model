import numpy as np
from regression import loadDataSet
from Get_Account import Get_Attribute

if __name__ == '__main__':
    w = []
    f = open('data/model.txt')
    text = f.readlines()
    Line = text[0].strip().split('\t')
    for i in Line: w.append(float(i))
    c = float(text[1])
    wmat = np.mat(w)
    dataset,ans = loadDataSet('data/Account_info.txt')
    Hatans = dataset * wmat.T + c
    #for i in range(0,1000):
        #print(int(Hatans[i,0]),' ',ans[i])
    n,m = np.shape(wmat)
    AttributeIndex = Get_Attribute()
    IndexAttribute = {}
    for key in AttributeIndex:
        IndexAttribute[int(AttributeIndex[key])] = key
    #print(IndexAttribute[1])
    for i in range(m):
        if(wmat[0,i] > 10):
            print(IndexAttribute[i])