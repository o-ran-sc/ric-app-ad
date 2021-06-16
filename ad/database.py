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

from influxdb import DataFrameClient


class Error(Exception):
    """Base class for other exceptions"""
    pass


class NoDataError(Error):
    """Raised when there is no data available in database for a given measurment"""
    pass


class DATABASE(object):
    r""" DATABASE takes an input as database name. It creates a client connection
      to influxDB and It reads/ writes UE data for a given dabtabase and a measurement.


    Parameters
    ----------
    host: str (default='localhost')
        hostname to connect to InfluxDB
    port: int (default='8086')
        port to connect to InfluxDB
    username: str (default='root')
        user to connect
    password: str (default='root')
        password of the use

    Attributes
    ----------
    client: influxDB client
        DataFrameClient api to connect influxDB
    data: DataFrame
        fetched data from database
    """

    def __init__(self, dbname, user='root', password='root', host='localhost', port='8086'):
        host = "10.104.162.154"
        self.client = DataFrameClient(host, port, user, password, dbname)
        self.data = None

    def read_data(self, meas, limit=100000):
        """Read data method for a given measurement and limit

        Parameters
        ----------
        limit:int (defualt=100000)
        """

        result = self.client.query('select * from ' + meas + ' limit ' + str(limit))
        print("Querying data : " + meas + " : size - " + str(len(result[meas])))
        try:
            if len(result[meas]) != 0:
                self.data = result[meas]
                self.data['measTimeStampRf'] = self.data.index
            else:
                raise NoDataError

        except NoDataError:
            print('Data not found for ' + meas + ' vnf')

    def write_anomaly(self, df, meas='AD'):
        """Write data method for a given measurement

        Parameters
        ----------
        meas: str (default='AD')
        """

        self.client.write_points(df, 'AD')
