# ==================================================================================
#       Copyright (c) 2020 HCL Technologies Limited.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ==================================================================================
from ad import main
from ricxappframe.xapp_frame import Xapp
from contextlib import suppress
import os
from ad.ad_train import train
import pandas as pd
from ad.ad_model.tb_format import parse
from ad.ad_model.ad_model import HDB_PREDICT
import json


def test_RFtrainmodel(monkeypatch):
    if not os.path.isfile('ad/RF'):
        train()


def test_predict_anomaly(monkeypatch):
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

    if len(val) > 2:
        assert val[3:7] == b'UEID'
        assert val[18:33] == b'MeasTimestampRF'


def test_msg_to_ts(monkeypatch, ad_to_ts):

    def mock_ad_entry(self):
        global val, mock_ad_xapp
        val = ad_to_ts
        mock_ad_xapp = Xapp(entrypoint=main.msg_to_ts(self, val), rmr_port=4564, use_fake_sdl=True)
        mock_ad_xapp.run()  # this will return since mock_ad_entry isn't a loop


def teardown_module():
    """
    this is like a "finally"; the name of this function is pytest magic
    safer to put down here since certain failures above can lead to pytest never returning
    for example if an exception gets raised before stop is called in any test function above,
    pytest will hang forever
    """
    with suppress(Exception):
        mock_ad_xapp.stop()
