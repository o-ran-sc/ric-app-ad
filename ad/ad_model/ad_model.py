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

import joblib
import random
import json


class modelling(object):
    def __init__(self, data):
        """ Separating UEID and timestamp features to be mapped later after prediction  """
        self.time = data.MeasTimestampRF
        self.id = data.UEID
        self.data = data.drop(['UEID', 'MeasTimestampRF'], axis=1)

    def predict(self, name):
        """
           Load the saved model and map the predicted category into Category field.
           Map UEID, MeasTimestampRF with the predicted result.
        """
        model = joblib.load('ad/' + name)
        pred = model.predict(self.data)
        data = self.data.copy()
        le = joblib.load('ad/LabelEncoder')
        data['Category'] = le.inverse_transform(pred)
        data['MeasTimestampRF'] = self.time
        data['UEID'] = self.id
        return data


def compare(df):
    """
     If the category of UEID is present in the segment file, it is considered as normal(0)
     otherwise, the sample is considered as anomaly.
    """
    with open("ad/ue_seg.json", "r") as json_data:
        segment = json.loads(json_data.read())
    anomaly = []
    for i in df.index:
        if df.loc[i, 'Category'] in segment[str(df.loc[i, 'UEID'])]:
            anomaly.append(0)
        else:
            anomaly.append(1)
    return anomaly


def HDB_PREDICT(df):
    """
        Extract all the unique UEID
        Call Predict method to get the final data for the randomly selected UEID
    """
    ue_list = df.UEID.unique()  # Extract unique UEIDs
    ue = random.choice(ue_list)  # Randomly selected the ue list
    df = df[df['UEID'] == ue]
    db = modelling(df)
    db_df = db.predict('RF')  # Calls predict module and store the result into db_df
    del db
    db_df['Anomaly'] = compare(db_df)
    return db_df
