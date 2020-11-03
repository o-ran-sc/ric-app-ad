import pandas as pd
import numpy as np
from scipy.stats import skew
import json
import joblib
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

class preprocess(object):
    
    def __init__(self,data):
        self.id = data.UEID
        self.time = data.MeasTimestampRF
        self.data = data.drop(['UEID','MeasTimestampRF'], axis = 1)

    #drop constant parameters
    def variation(self):
        self.data =  self.data.loc[:,self.data.apply(pd.Series.nunique) != 1]
    
    
    def numerical_data(self):
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        self.data =  self.data.select_dtypes(include=numerics)
    
    #drop observations having nan values
    def drop_na(self):
        self.data = self.data.dropna(axis=0)

 

    #chek and drop high correlation parameters
    def correlation(self):
        corr = self.data.corr().abs()
        corr = pd.DataFrame(np.tril(corr, k =-1), columns = self.data.columns)
        drop = [column for column in corr.columns if any(corr[column] > 0.98)]
        self.data = self.data.drop(drop,axis=1)
    
    #check skewness of all parameters and use log transform if half of parameters are enough skewd
    #otherwise use standardization
    def transform(self):
        #self.data = self.data.abs()
        #self.data=self.data.applymap(lambda x: np.log(x+1))
        scale = StandardScaler()
        data = scale.fit_transform(self.data)
        self.data = pd.DataFrame(data, columns = self.data.columns)
        joblib.dump(scale, '/tmp/ad/scale')

    #normalize the data
    def normalize(self):
        upper = self.data.max()
        lower = self.data.min()
        self.data = (self.data - lower)/(upper-lower)  
    

    def process(self):
        self.numerical_data()
        self.drop_na()
        self.variation()
#        self.correlation()
        self.transform()
        self.data.loc[:,'UEID'] = self.id      
        self.data.loc[:,'MeasTimestampRF'] = self.time
        return self.data
