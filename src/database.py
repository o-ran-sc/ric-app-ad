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
import time
import pandas as pd
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from configparser import ConfigParser
from mdclogpy import Logger
from urllib3.exceptions import HTTPError

logger = Logger(name=__name__)


class DATABASE(object):
    r""" DATABASE takes an input as database name. It creates a client connection
      to influxDB v2 and reads/writes UE data for a given bucket and measurement.

    Parameters
    ----------
    url: str (default='http://ricplt-influxdb.ricplt:8086')
        InfluxDB v2 URL
    token: str (default='client')
        authentication token
    org: str (default='my-org')
        InfluxDB organization
    bucket: str (default='kpimon')
        InfluxDB bucket name

    Attributes
    ----------
    client: InfluxDBClient
        InfluxDB v2 client
    data: DataFrame
        fetched data from database
    """

    def __init__(self, url='http://ricplt-influxdb.ricplt:8086', token='client', org='my-org', bucket='kpimon'):
        self.data = None
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.meas = 'UeMetrics'
        self.client = None
        self.config()

    def connect(self):
        if self.client is not None:
            self.client.close()

        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            health = self.client.health()
            if health.status == "pass":
                logger.info("Connected to InfluxDB v2, status: {}".format(health.status))
                return True
            else:
                logger.error("InfluxDB health check failed: {}".format(health.message))
                time.sleep(120)
                return False

        except Exception as e:
            logger.error("Failed to establish a new connection with InfluxDB: {}".format(e))
            time.sleep(120)
            return False

    def read_data(self, train=False, valid=False, limit=False):
        """Read data method for a given measurement and limit

        Parameters
        ----------
        train: bool  (use training time range)
        valid: bool  (use validation time range)
        limit: int   (limit number of records)
        """
        self.data = None

        if not train and not valid and not limit:
            time_range = 'start: -2s'
        elif train:
            time_range = 'start: -75m, stop: -5m'
        elif valid:
            time_range = 'start: -5m'
        elif limit:
            time_range = 'start: -1m'

        flux_query = (
            f'from(bucket: "{self.bucket}")'
            f' |> range({time_range})'
            f' |> filter(fn: (r) => r._measurement == "{self.meas}")'
            f' |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
        )
        if limit:
            flux_query += f' |> limit(n: {limit})'

        result = self.query(flux_query)
        if result is not None and len(result) > 0:
            self.data = result

    def write_anomaly(self, df, meas='AD'):
        """Write data method for a given measurement

        Parameters
        ----------
        df: DataFrame
        meas: str (default='AD')
        """
        try:
            write_api = self.client.write_api(write_options=SYNCHRONOUS)
            write_api.write(
                bucket=self.bucket,
                org=self.org,
                record=df,
                data_frame_measurement_name=meas,
            )
        except Exception as e:
            logger.error('Failed to send metrics to influxdb: {}'.format(e))

    def query(self, flux_query):
        try:
            query_api = self.client.query_api()
            result = query_api.query_data_frame(flux_query, org=self.org)
            if isinstance(result, list):
                result = pd.concat(result, ignore_index=True) if result else pd.DataFrame()
            if not result.empty:
                # Clean up influx metadata columns
                drop_cols = [c for c in ['result', 'table', '_start', '_stop', '_measurement'] if c in result.columns]
                result.drop(columns=drop_cols, inplace=True)
                if '_time' in result.columns:
                    result.set_index('_time', inplace=True)
                    result.index.name = 'time'
            return result
        except Exception as e:
            logger.error('Failed to query influxdb: {}'.format(e))
            return None

    def config(self):
        cfg = ConfigParser()
        cfg.read('src/ad_config.ini')
        for section in cfg.sections():
            if section == 'influxdb':
                self.url = cfg.get(section, "url")
                self.token = cfg.get(section, "token")
                self.org = cfg.get(section, "org")
                self.bucket = cfg.get(section, "bucket")
                self.meas = cfg.get(section, "measurement")

            if section == 'features':
                self.thpt = cfg.get(section, "thpt")
                self.rsrp = cfg.get(section, "rsrp")
                self.rsrq = cfg.get(section, "rsrq")
                self.rssinr = cfg.get(section, "rssinr")
                self.prb = cfg.get(section, "prb_usage")
                self.ue = cfg.get(section, "ue")
                self.anomaly = cfg.get(section, "anomaly")
                self.a1_param = cfg.get(section, "a1_param")


class DUMMY(DATABASE):

    def __init__(self):
        super().__init__()
        self.ue_data = pd.read_csv('src/ue.csv')

    def connect(self):
        return True

    def read_data(self, train=False, valid=False, limit=100000):
        if not train:
            self.data = self.ue_data.head(limit)
        else:
            self.data = self.ue_data.head(limit).drop(self.anomaly, axis=1)

    def write_anomaly(self, df, meas_name='AD'):
        pass

    def query(self, query=None):
        return {'UEReports': self.ue_data.head(1)}
