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
from ad_model.processing import preprocess
import json, datetime

UEKeyList = ['MeasTimestampRF','UEPDCPBytesDL','Category', 'UEPDCPBytesUL', 'UEPRBUsageDL', 'UEPRBUsageUL','S_RSRP', 'S_RSRQ', 'S_SINR','UEID']

def parse(df):
    """
      This block will be modified when we are going to fetch the data from database via sdl api.

      start the preprocessing, processing steps using the keycolumns
      populates the current timestamp value for MeasTimestampRF
    """
    df.index = range(df.shape[0])
    df = df[UEKeyList]
    db = preprocess(df)
    df = db.process()
    del db
    df['MeasTimestampRF'] = pd.date_range(start = datetime.datetime.now(), periods = len(df), freq = '-10ms')
    return df
