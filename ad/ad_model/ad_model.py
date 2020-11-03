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
import numpy as np
import joblib
import random

class modelling(object):
    def __init__(self,data):
        """ Separating UEID, Category and timestamp features to be mapped later after prediction  """
        self.time = data.MeasTimestampRF
        self.id = data.UEID
        self.cat = data.Category
        self.data = data.drop(['UEID','Category', 'MeasTimestampRF'], axis = 1)
        
    def predict(self, name):
        """  
           Load the saved model(hdbscan)
           Do the prediction and use the invert transformation
           Map UEID, MeasTimestampRF with the predicted result. 
        """
        model = joblib.load(name)
        label, strengths = hdbscan.approximate_predict(model, self.data)
        data = self.data.copy()
        data = data.apply(lambda x: np.exp(x) -1)
        data.loc[:, 'Anomaly'] = label 
        data['MeasTimestampRF'] = self.time
        data['UEID'] = self.id
        data['Category'] = self.cat
        return data
    
def HDB_PREDICT(df):
    """
        Extract all the unique UEID 
        Call Predict method to get the final data for the randomly selected UEID
    """
    ue_list = df.UEID.unique()  # Extract unique UEIDs
    ue = random.choice(ue_list) # Randomly selected the ue list
    df = df[df['UEID'] == ue]
    db = modelling(df)
    db_df = db.predict('/tmp/ad/hdbscan')  # Calls predict module and store the result into db_df
    del db
    return db_df
