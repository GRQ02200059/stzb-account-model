import numpy as np

dic = {'asd':1}
x = np.zeros((5))
x[dic['asd']] = 2
x[1] = 3
print(x)