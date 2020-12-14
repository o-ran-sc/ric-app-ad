import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler


class preprocess(object):

    def __init__(self, data):
        """
           Columns that are not useful for the prediction will be dropped(UEID, Category, & Timestamp)
        """
        self.id = data.UEID
        self.time = data.MeasTimestampRF
        self.data = data.drop(['UEID', 'MeasTimestampRF'], axis=1)

    def variation(self):
        """ drop the constant parameters """
        self.data = self.data.loc[:, self.data.apply(pd.Series.nunique) != 1]

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
    def transform(self):
        """ use log transform for skewed data """
        scale = StandardScaler()
        data = scale.fit_transform(self.data)
        self.data = pd.DataFrame(data, columns=self.data.columns)
        joblib.dump(scale, 'ad/scale')

    def process(self):
        """
          Calls the modules for the data preprocessing like dropping columns, normalization etc.,
        """
        self.numerical_data()
        self.drop_na()
        self.variation()
#        self.correlation()
        self.transform()
        self.data.loc[:, 'UEID'] = self.id
        self.data.loc[:, 'MeasTimestampRF'] = self.time
        return self.data
