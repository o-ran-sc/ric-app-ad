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
from ricxappframe.xapp_frame import Xapp
#from ad import main

def test_init_adxapp(monkeypatch):

    # start ad
    #main.predict()

    # rmr send 30003(TS_ANOMALY_UPDATE), should trigger registered callback
    
    val = '[{"UEID": 12419, "MeasTimestampRF": "2020-11-11 13:28:25.135743"}]'
    self.rmr_send(val, 30003)

    # rmr receive to get the acknowledgement message from the traffic steering.
    for (summary, sbuf) in self.rmr_get_messages():
        print("TS_ANOMALY_ACK: {}".format(summary))
        self.rmr_free(sbuf)
    

