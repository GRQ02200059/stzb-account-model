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
    #for i in range(0,3000):
        #print(int(Hatans[i,0]),' ',ans[i])
    n,m = np.shape(wmat)
    AttributeIndex = Get_Attribute()
    IndexAttribute = {}
    for key in AttributeIndex:
        IndexAttribute[int(AttributeIndex[key])] = key
    sorted_nums = sorted(enumerate(w), key=lambda x: x[1])
    idx = [i[0] for i in sorted_nums]
    nums = [i[1] for i in sorted_nums]
    #print(idx)
    for i in idx:
        print(IndexAttribute[i],'   ',w[i])
    #print(IndexAttribute[i])