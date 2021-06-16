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
from ad_model.processing import PREPROCESS
from sklearn.metrics import classification_report, f1_score
from pyod.models.iforest import IForest
from database import DATABASE
import numpy as np


class modelling(object):
    r""" The modelling class takes input as dataframe or array and train Isolation Forest model

    Paramteres
    .........
    data: DataFrame or array
        input dataset
    cols: list
        list of parameters in input dataset

    Attributes
    ----------
    actual:array
        actual label for test data
    X: DataFrame or array
        transformed values of input data
    """
    def __init__(self, data):
        self.data = data
        self.cols = data.columns
        self.read_test()

    def read_test(self):
        """ Read test dataset for model validation"""

        db = DATABASE('UEData')
        db.read_data('valid')
        test = db.data
        self.actual = test['Anomaly']
        X = test[self.cols]
        sc = joblib.load('scale')
        self.X = sc.transform(X)

    def isoforest(self, outliers_fraction=0.05, random_state=42, push_model=False):
        """ Train isolation forest

        Parameters
        ----------
        outliers_fraction: float between 0.01 to 0.5 (default=0.05)
            percentage of anomalous available in input data
        push_model: boolean (default=False)
            return f_1 score if True else push model into repo
        random_state: int (default=42)
        """
        iso = IForest(contamination=outliers_fraction, random_state=random_state)
        md = iso.fit(self.data, None)
        if push_model:
            joblib.dump(self.cols, 'params')
            joblib.dump(md, 'model')
        return test(self, md, m=push_model)


def train():
    """
     Main function to perform training on input data
    """

    db = DATABASE('UEData')
    db.read_data('train')
    ps = PREPROCESS(db.data)
    ps.process()
    df = ps.data

    db = modelling(df)
    scores = []
    for of in np.arange(0.01, 0.2, 0.01):
        scores.append(db.isoforest(outliers_fraction=of))
    opt_f1 = scores.index(max(scores)) + 1
    db.isoforest(outliers_fraction=opt_f1*0.01, push_model=True)
    print("Optimum value of contamination : {}".format(opt_f1*0.01))
    print('Training Ends : ')


def test(self, model, m=None):
    pred = model.predict(self.X)
    if -1 in pred:
        pred = [1 if p == -1 else 0 for p in pred]
    if m:
        print(classification_report(self.actual, pred))
    return f1_score(self.actual, pred)
