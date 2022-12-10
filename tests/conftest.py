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
import pytest
import pandas as pd


@pytest.fixture
def ad_to_ts():
    ad_to_ts_val = '[{"du-id": 1006, "ue-id": "Car-1", "measTimeStampRf": 1620832626630, "Degradation": "RSRP"}]'
    return ad_to_ts_val


@pytest.fixture
def ad_ue():
    ad_ue_val = pd.DataFrame([[1002, "c2/B13", 8, 69, 65, 113, 0.1, 0.1, "Waiting passenger 9", -882, -959, pd.to_datetime("2021-05-12T07:43:51.652")]], columns=["du-id", "ServingCellId", "RRU.PrbUsedDl", "RF.serving.RSRP", "RF.serving.RSRQ", "RF.serving.RSSINR", "TargetTput", "DRB.UEThpDl", "ue-id", "x", "y", "measTimeStampRf"])

    return ad_ue_val
