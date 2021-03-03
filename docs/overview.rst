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


Anomaly Detection Overview
==========================

Anomaly Detection (AD) is an Xapp in the Traffic Steering O-RAN use case,
which uses the following Xapps:

#. AD, which iterates per second, fetches UE data from .csv files and send prediction to Traffic Steering
#. Traffic Steering send acknowldgement back to AD.

Expected Input
--------------

The AD Xapp expects a prediction-input in following structure:

UEPDCPBytesDL  UEPDCPBytesUL  UEPRBUsageDL  UEPRBUsageUL  S_RSRP  S_RSRQ  S_SINR  N1_RSRP  N1_RSRQ  N1_SINR  N2_RSRP  N2_RSRQ  N2_SINR  UEID  ServingCellID     N1      N2      MeasTimestampRF

  300000         123000 	  25		10	   -43     -3.4     25	    -5	    -6.4      20       -68	-9.4      17	12345	  555011      555010   555012       30:17.8
	

Expected Output
---------------

The AD Xapp should send a prediction for Anomulous UEID along with timestamp
as a JSON message via RMR with the following structure:

  {
  "UEID" : 12371,
  "MeasTimestampRF" : "2020-11-17 16:14:25.140140"
  }

  
