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

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import Normalizer


class PREPROCESS(object):
    r""" This PREPROCESS class takes raw data and apply prepocessing on to that.

    Parameters
    ----------
    data: pandas dataframe
        input dataset to process in pandas dataframe

    Attributes
    ----------
    data: DataFrame
        DataFrame that has processed data
    temp: list
        list of attributes to drop
    """

    def __init__(self, data):
        """
           Columns that are not useful for the prediction will be dropped(UEID, Category, & Timestamp)
        """
        self.data = data
        self.convert_gb_to_mb()

    def variation(self):
        """ drop the constant parameters """
        if len(self.data) > 1:
            self.data = self.data.loc[:, self.data.apply(pd.Series.nunique) != 1]

    def convert_gb_to_mb(self):
        self.data.iloc[:]['DRB.UEThpDl'] = self.data['DRB.UEThpDl'].apply(lambda x: x*1024)

    def numerical_data(self):
        """  Filters only numeric data types """
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        self.data = self.data.select_dtypes(include=numerics)

    def drop_na(self):
        """ drop observations having nan values """
        self.data = self.data.dropna(axis=0)

    def correlation(self):
        """  check and drop high correlation parameters  """
        corr = self.data.corr().abs()
        corr = pd.DataFrame(np.tril(corr, k=-1), columns=self.data.columns)
        drop = [column for column in corr.columns if any(corr[column] > 0.98)]
        self.data = self.data.drop(drop, axis=1)

    # check skewness of all parameters and use log transform if half of parameters are enough skewd
    # otherwise use standardization
    def fit_transform(self):
        """ use normalizer transformation to bring all parameters in same scale """
        scale = Normalizer().fit(self.data)
        joblib.dump(scale, 'src/scale')

    def transform(self):
        scale = joblib.load('src/scale')
        self.data = pd.DataFrame(scale.transform(self.data), columns=self.data.columns)

    def save_cols(self):
        joblib.dump(self.data.columns, 'src/num_params')

    def process(self):
        """
          Calls the modules for the data preprocessing like dropping columns, normalization etc.,
        """
        temp = []
        for col in self.data.columns:
            if 'nb' in col or 'Geo' in col or 'anomal' in col or 'target' in col:
                temp.append(col)
        self.data = self.data.drop(temp, axis=1)
        self.numerical_data()
        self.drop_na()
        self.variation()
        self.correlation()
        self.fit_transform()
        self.transform()
        self.save_cols()
