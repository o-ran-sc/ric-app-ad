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

import json
import os
from ricxappframe.xapp_frame import Xapp
import pandas as pd
from ad_model.ad_model import ad_predict, Cause
import schedule
from ad_train import train
from ricxappframe.xapp_sdl import SDLWrapper
from database import DATABASE

db = DATABASE('UEData')
cp = Cause()
db.read_data("liveUE")
ue_data = db.data.values.tolist()  # needs to be updated in future when live feed will be coming through KPIMON to influxDB
pos = 0
NS = "TS-UE-metrics-second"
sdl = SDLWrapper(use_fake_sdl=True)


def entry(self):
    """  If ML model is not present in the path, It will trigger training module to train the model.
      Calls predict function every 10 milisecond(for now as we are using simulated data).
    """
    if not os.path.isfile('model'):
        train()
    schedule.every(0.01).seconds.do(predict, self)
    while True:
        schedule.run_pending()


def predict(self):
    """Read the latest ue sample from influxDB and detects if that is anomalous or normal..
      Send the UEID, DUID, Degradation type and timestamp for the anomalous samples to Traffic Steering (rmr with the message type as 30003)
      Get the acknowledgement of sent message from the traffic steering.
    """

    global pos
    pos = (pos + 1) % len(ue_data)  # iterate through entire list one by one in cycle manner and will be updated when live feed will be coming through KPIMON to influxDB
    sample = ue_data[pos]
    val = predict_anomaly(sample)
    if (val is not None) and (len(val) > 2):
        msg_to_ts(self, val)


def predict_anomaly(ue):
    """ calls ad_predict to detect if given sample is normal or anomalous
    find out the degradation type if sample is anomalous
    write given sample along with predicted label to AD measurement

    Parameter
    ........
    ue: array or dataframe

    Return
    ......
    val: anomalus sample info(UEID, DUID, TimeStamp, Degradation type)
    """
    df = pd.DataFrame([ue], columns=db.data.columns)
    pred = ad_predict(df)
    df['Anomaly'] = pred
    df['Degradation'] = ''
    val = None
    if 1 in pred:
        deg = cp.cause(df)
        if deg:
            df['Degradation'] = deg
            db_df = df[['du-id', 'ue-id', 'measTimeStampRf', 'Degradation']]

            # rmr send 30003(TS_ANOMALY_UPDATE), should trigger registered callback
            result = json.loads(db_df.to_json(orient='records'))
            val = json.dumps(result).encode()
            df.loc[db_df.index, 'Degradation'] = db_df['Degradation']
    df.index = df.measTimeStampRf
    df = df.drop('measTimeStampRf', axis=1)
    db.write_anomaly(df, 'AD')
    return val


def msg_to_ts(self, val):
    # send message from ad to ts
    print("rmr send value(debug purpose):", val)
    self.rmr_send(val, 30003)

    # rmr receive to get the acknowledgement message from the traffic steering.
    for (summary, sbuf) in self.rmr_get_messages():
        print("TS_ANOMALY_ACK: {}".format(summary))
        self.rmr_free(sbuf)


def start():
    # Initiates xapp api and runs the entry() using xapp.run()
    xapp = Xapp(entrypoint=entry, rmr_port=4560, use_fake_sdl=True)
    xapp.run()
