# ==================================================================================
#  Copyright (c) 2020 HCL Technologies Limited.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ==================================================================================
import warnings
import json
import hdbscan
import pandas as pd
import numpy as np
import joblib, os
from ad_model.processing import preprocess
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix,f1_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Ranges for input features based on excellent, good, average, & poor category
UEKeyList = ['MeasTimestampRF','UEPDCPBytesDL', 'UEPDCPBytesUL', 'UEPRBUsageDL', 'UEPRBUsageUL', 'S_RSRP', 'S_RSRQ', 'S_SINR','UEID']
#UEKeyList = ['S_RSRP', 'S_RSRQ', 'S_SINR','UEID','MeasTimestampRF']

sigstr = {'S_RSRP': {'Excellent Signal' : [-80, 10000000000000000], 'Good Signal': [-90,-80], 'Average Signal':[-100,-90], 'Poor Signal':[-100000000000000000,-100]}, 'S_RSRQ' : {'Excellent Signal' : [-10, 10000000000000000], 'Good Signal': [-15,-10], 'Average Signal':[-20,-15], 'Poor Signal':[-100000000000000000,-20]}, 'S_SINR' : {'Excellent Signal' : [20, 10000000000000000], 'Good Signal': [13,20], 'Average Signal':[0,13], 'Poor Signal':[-100000000000000000,0]}}

PRB = {'UEPRBUsageDL': {'Excellent Signal' : [25, 10000000000000000], 'Good Signal': [20,25], 'Average Signal':[10,20], 'Poor Signal':[-100000000000000000,10]}, 'UEPRBUsageUL' : {'Excellent Signal' : [15, 10000000000000000], 'Good Signal': [10,15], 'Average Signal':[5,10], 'Poor Signal':[-100000000000000000,5]}}

tput = {'UEPDCPBytesDL': {'Excellent Signal' : [300000, 10000000000000000], 'Good Signal': [200000,300000], 'Average Signal':[100000,200000], 'Poor Signal':[-100000000000000000,100000]}, 'UEPDCPBytesUL' : {'Excellent Signal' : [125000, 10000000000000000], 'Good Signal': [100000,125000], 'Average Signal':[10000,100000], 'Poor Signal':[-100000000000000000,10000]}}


def category(df,ranges):
    """
     Based on ranges, each sample is return with category(excellent, good, average, & poor category).
    """
    data = df.copy()
    for block in ranges:
        df = data[list(block.keys())].copy()
        for key, value in block.items():
            temp = data[list(block.keys())].copy()
            for cat, bounds in value.items():
                ind = temp[(temp[key] <= bounds[1]) & (temp[key] > bounds[0])].index
                df.loc[ind, key] = cat
        data[df.columns] = df
    category =  data[['UEPDCPBytesDL', 'UEPDCPBytesUL', 'UEPRBUsageDL', 'UEPRBUsageUL',
       'S_RSRP', 'S_RSRQ', 'S_SINR']].mode(axis = 1)[0]
    return category


class modelling(object):
    def __init__(self,data):
        self.time = data.MeasTimestampRF
        self.id = data.UEID
        self.data = data.drop(['UEID', 'MeasTimestampRF'], axis = 1)
        
    def dbscan(self):
        """
         Train hdbscan for the input dataframe
         save the hdbscan model
        """        
        df = self.data.copy()
        hdb = hdbscan.HDBSCAN(min_cluster_size=16000, min_samples = 5, prediction_data = True).fit(df)
        joblib.dump(hdb, '/tmp/ad/hdbscan')
        self.data['Category'] = hdb.labels_

    def RandomForest(self, y):
        """
         Transform categorical label into numeric(Save the LabelEncoder).
         Create Train and Test split for Random Forest Classifier and Save the model
        """
        df = self.data.copy()
        le = LabelEncoder()
        y = le.fit_transform(y)
        joblib.dump(le, '/tmp/ad/LabelEncoder')
        X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.20, stratify=y, random_state=42)
        rf = RandomForestClassifier(max_depth=9, random_state=0)
        rf.fit(X_train, y_train)
        
        joblib.dump(rf, '/tmp/ad/RF')
        print('--------------------------- Training Score------------------------------------')
        score(X_test, y_test, rf)
        print('--------------------------- Test Score------------------------------------')
        test = pd.read_csv('/tmp/ad/ue_test.csv')
        test = test[UEKeyList]
        y = category(test, [sigstr, PRB, tput])
        y =le.transform(y)
        ps = preprocess(test)
        ps.process()
        test = ps.data.drop(['UEID', 'MeasTimestampRF'], axis = 1)
        score(test, y, rf)

def score(X, y, model):
    y_pred = model.predict(X)
    print('Accuracy : {}'.format(accuracy_score(y, y_pred)))

    print('confusion matrix : {}'.format(confusion_matrix(y, y_pred)))
    print('f1-score : {}'.format(f1_score(y, y_pred, average = 'macro')))


def train():
    """
     Main function to perform training on input files
     Read all the csv file in the current path and create trained model
    """    
    print('Training Starts : ')
    path = '/tmp/ad/ue_data/'
    df = pd.DataFrame()
    # Read all the csv files and store the combined data into df
    for file in os.listdir(path):
        df = df.append(pd.read_csv(path + file))
    
    df = df[UEKeyList]
    df.index = range(len(df))
    y =  category(df, [sigstr, PRB, tput])
    seg = {}

    #Save the category of each UEID and save it as json file
    for ue in df.UEID.unique():
        seg[str(ue)] = list(set(y[df[df['UEID'] == ue].index]))
    
    with open('ue_seg.json', 'w') as outfile:
        json.dump(seg, outfile)

    # Do a preprocessing, processing and save the model
    ps = preprocess(df)
    ps.process()
    df = ps.data
    db = modelling(df)
#    db.dbscan()
    db.RandomForest(y)
