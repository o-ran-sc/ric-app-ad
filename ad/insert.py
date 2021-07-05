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

"""
This Module is temporary for pushing data into influxdb when AD xApp starts. It will depreciated in future, when data will be coming through KPIMON
"""

import pandas as pd
from influxdb import DataFrameClient
import datetime


class INSERTDATA:

    def __init__(self):
        host = 'r4-influxdb.ricplt'
        self.client = DataFrameClient(host, '8086', 'root', 'root')
        self.dropdb('UEData')
        self.createdb('UEData')

    def createdb(self, dbname):
        print("Create database: " + dbname)
        self.client.create_database(dbname)
        self.client.switch_database(dbname)

    def dropdb(self, dbname):
        print("DROP database: " + dbname)
        self.client.drop_database(dbname)

    def dropmeas(self, measname):
        print("DROP MEASUREMENT: " + measname)
        self.client.query('DROP MEASUREMENT '+measname)


def explode(df):
    for col in df.columns:
        if isinstance(df.iloc[0][col], list) and col != 'neighbourCellList':
            df = df.explode(col)
        d = df[col].apply(pd.Series)
        if col in list(range(5)):
            d.columns = d.columns + '_' + str(col)
        elif 'nbCellRfReport_' in col:
            d.columns = d.columns + '_nb_' + col[-1]
        df[d.columns] = d
        df = df.drop(col, axis=1)
    return df


def jsonToTable(df):
    df.index = range(len(df))
    cols = [col for col in df.columns if isinstance(df.iloc[0][col], dict) or isinstance(df.iloc[0][col], list)]
    if len(cols) == 0:
        return df
    for col in cols:
        d = explode(pd.DataFrame(df[col], columns=[col]))
        d = d.dropna(axis=1, how='all')
        df = pd.concat([df, d], axis=1)
        df = df.drop(col, axis=1).dropna()
    return jsonToTable(df)


def time(df):
    df.index = pd.date_range(start=datetime.datetime.now(), freq='10ms', periods=len(df))
    df['measTimeStampRf'] = df['measTimeStampRf'].apply(lambda x: str(x))
    return df


def populatedb():
    data = pd.read_csv('ad/valid.csv')
    data = time(data)

    # inintiate connection and create database UEDATA
    db = INSERTDATA()
    db.client.write_points(data, 'valid')
    del data

    df = pd.read_json('ad/ue.json.gz', lines=True)
    df = df[['ueMeasReport']].dropna()
    df = jsonToTable(df)
    df = time(df)

    db.client.write_points(df, 'train', batch_size=500,  protocol='line')
    db.client.write_points(df, 'liveUE', batch_size=500, protocol='line')
