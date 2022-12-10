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
import json
from src import main
from ricxappframe.xapp_frame import Xapp
from contextlib import suppress


def test_database_connection(monkeypatch):
    # start ad
    main.connectdb(thread=True)


def test_trainModel(monkeypatch):
    main.train_model()


def test_predict_anomaly(monkeypatch, ad_ue):
    main.load_model()
    main.predict_anomaly(monkeypatch, ad_ue)


def test_msg_to_ts(monkeypatch, ad_to_ts):

    def mock_ad_entry(self):
        val = json.dumps(ad_to_ts).encode()
        self.rmr_send(val, 30003)
    global mock_ad_xapp
    mock_ad_xapp = Xapp(entrypoint=mock_ad_entry, rmr_port=4564, use_fake_sdl=True)
    mock_ad_xapp.run()  # this will return since mock_ad_entry isn't a loop  # this will return since mock_ad_entry isn't a loop


def teardown_module():
    """
    this is like a "finally"; the name of this function is pytest magic
    safer to put down here since certain failures above can lead to pytest never returning
    for example if an exception gets raised before stop is called in any test function above,
    pytest will hang forever
    """
    with suppress(Exception):
        mock_ad_xapp.stop()
