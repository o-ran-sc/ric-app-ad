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

import hdbscan
import pandas as pd
import joblib, os
from ad_model.processing import preprocess

UEKeyList = ['MeasTimestampRF', 'Category', 'UEPDCPBytesDL', 'UEPDCPBytesUL', 'UEPRBUsageDL', 'UEPRBUsageUL', 'S_RSRP', 'S_RSRQ', 'S_SINR','UEID']

class modelling(object):
    def __init__(self,data):
        self.id = data.UEID
        self.data = data.drop(['UEID', 'MeasTimestampRF', 'Category'], axis = 1)
        
    def dbscan(self):
        """ 
         Train hdbscan for the input dataframe(all categories except poor signal)
         save the hdbscan model 
        """
        df = self.data.copy()
        hdb = hdbscan.HDBSCAN(min_cluster_size=18000, min_samples = 5, prediction_data = True).fit(df)
        joblib.dump(hdb, 'hdbscan')


def train():
    """
     Read all the files from the below directory(csv files)
     Do porcessing and train hdbscan on all categories except poor signal
     Save the model     
    """
    path = '/tmp/ad/ue_data/'
    df = pd.DataFrame()
    for file in os.listdir(path):
        df = df.append(pd.read_csv(path + file))
    df = df[UEKeyList]
    df = df[df['Category']!='Poor Signal']
    ps = preprocess(df)
    ps.process()
    df = ps.data
    db = modelling(df)
    db.dbscan()


