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
from ad_model.tb_format import parse
from ad_model.ad_model import HDB_PREDICT
import schedule
from ad_train import train


def entry(self):
    """
      If RF model is not present in the path, run train() to train the model for the prediction.
      Calls predict function for every 1 second(for now as we are using simulated data).
    """
    if not os.path.isfile('ad/RF'):
        train()
    schedule.every(1).seconds.do(predict, self)
    while True:
        schedule.run_pending()


def predict(self):
    """
      Read the input csv file that has both normal and anomalous data.
      Simulate diff UEIDs that participate in the anomaly by randomly selecting records from this scoring data set
      Send the UEID and timestamp for the anomalous entries to the Traffic Steering (rmr with the message type as 30003)
      Get the acknowledgement message from the traffic steering.
    """
    val = predict_anomaly(self)
    if len(val) > 2:
        msg_to_ts(self, val)


def predict_anomaly(self):
    # The read_csv logic will be modified when we are going to fetch the data from database via sdl api.
    # Read the input csv file
    ue_data = pd.read_csv('ad/ue_test.csv')

    # Parse the ue data and predict the anomaly records for the randomly selected UEID
    data = parse(ue_data)
    db_df = HDB_PREDICT(data)
    db_df = db_df.loc[db_df['Anomaly'] == 1][['UEID', 'MeasTimestampRF']].head(1)
    db_df['MeasTimestampRF'] = db_df['MeasTimestampRF'].apply(lambda x: str(x))  # converts into string format

    # rmr send 30003(TS_ANOMALY_UPDATE), should trigger registered callback
    result = json.loads(db_df.to_json(orient='records'))
    val = json.dumps(result).encode()
    return val


def msg_to_ts(self, val):
    # send message from ad to ts
    print("rmr send value:", val)
    self.rmr_send(val, 30003)

    # rmr receive to get the acknowledgement message from the traffic steering.
    for (summary, sbuf) in self.rmr_get_messages():
        print("TS_ANOMALY_ACK: {}".format(summary))
        self.rmr_free(sbuf)


def start():
    # Initiates xapp api and runs the entry() using xapp.run()
    xapp = Xapp(entrypoint=entry, rmr_port=4560, use_fake_sdl=True)
    xapp.run()
