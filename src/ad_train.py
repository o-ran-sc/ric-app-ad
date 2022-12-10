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
import time
import numpy as np
from processing import PREPROCESS
from sklearn.metrics import classification_report, f1_score
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import RandomizedSearchCV
from mdclogpy import Logger

logger = Logger(name=__name__)


class ModelTraining(object):
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
    def __init__(self, db):
        self.db = db
        self.train_data = None
        self.test_data = None
        self.read_train()
        self.read_test()

    def read_train(self):
        self.db.read_data(train=True)
        while self.db.data is None or len(self.db.data.dropna()) < 1000:
            logger.warning("Check if InfluxDB instance is up / Not sufficient data for Training")
            time.sleep(120)
            self.db.read_data(train=True)
        self.train_data = self.db.data
        logger.debug("Training on {} Samples".format(self.train_data.shape[0]))

    def read_test(self):
        """ Read test dataset for model validation"""
        self.db.read_data(valid=True)
        while self.db.data is None or len(self.db.data.dropna()) < 300:
            logger.warning("Check if InfluxDB instance is up? or Not sufficient data for Validation in last 10 minutes")
            time.sleep(60)
            self.db.read_data(valid=True)
        self.test_data = self.db.data.dropna()
        logger.debug("Validation on {} Samples".format(self.test_data.shape[0]))

    def isoforest(self, outliers_fraction=0.05, random_state=4):
        """ Train isolation forest

        Parameters
        ----------
        outliers_fraction: float between 0.01 to 0.5 (default=0.05)
            percentage of anomalous available in input data
        push_model: boolean (default=False)
            return f_1 score if True else push model into repo
        random_state: int (default=42)
        """
        parameter = {'contamination': [of for of in np.arange(0.01, 0.5, 0.02)],
                     'n_estimators': [100*(i+1) for i in range(1, 10)],
                     'max_samples': [0.005, 0.01, 0.1, 0.15, 0.2, 0.3, 0.4]}
        cv = [(slice(None), slice(None))]
        iso = IsolationForest(random_state=random_state, bootstrap=True, warm_start=False)
        model = RandomizedSearchCV(iso, parameter, scoring=self.validate, cv=cv, n_iter=50)
        md = model.fit(self.train_data.values)
        f1 = self.validate(md.best_estimator_, self.test_data, True)
        return f1, md.best_estimator_

    def validate(self, model, test_data, report=False):
        pred = model.predict(self.test_data.values)
        if -1 in pred:
            pred = [1 if p == -1 else 0 for p in pred]
        F1 = f1_score(self.actual, pred, average='macro')
        if report:
            logger.debug("classfication report : {} ".format(classification_report(self.actual, pred)))
            logger.debug("F1 score:{}".format(F1))
        return F1

    def train(self):
        """
        Main function to perform training on input data
        """
        logger.debug("Training Starts")
        ps = PREPROCESS(self.train_data)
        ps.process()
        self.train_data = ps.data

        self.actual = (self.test_data[self.db.anomaly] > 0).astype(int)
        num = joblib.load('src/num_params')
        ps = PREPROCESS(self.test_data[num])
        ps.transform()
        self.test_data = ps.data

        scores = []
        models = []

        logger.info("Training Isolation Forest")
        f1, model = self.isoforest()
        scores.append(f1)
        models.append(model)

        opt = scores.index(max(scores))
        joblib.dump(models[opt], 'src/model')
        logger.info("Optimum f-score : {}".format(scores[opt]))
        logger.info("Training Ends : ")
