
Anomaly Detection Overview
======================

Anomaly Detection (AD) is an Xapp in the Traffic Steering O-RAN use case,
which uses the following Xapps:

#. AD, which iterates per second, fetches UE data from .csv files and send prediction to Traffic Steering
#. Traffic Steering send acknowldgement back to AD.

Expected Input
--------------

The AD Xapp expects a prediction-input in following structure:

  {
  'du-id' : 1003,
  'nrCellIdentity' : "c3/B13",
  'prb_usage' : 23.0, 
  'rsrp' : 84.0, 
  'rsrq' : 65.0, 
  'rssinr':65.0,
  'targetTput' : 0.1, 
  'throughput' : , 
  'ue-id' : "Waiting passenger 1", 
  'x' : -556, 
  'y' : -1160, 
  'measTimeStampRf' : "2021-05-12T07:43:51.652" 
  }

Expected Output
---------------

The AD Xapp should send a prediction for Anomulous UEID along with timestamp
as a JSON message via RMR with the following structure:

  {
  'ue-id' : "Waiting passenger 1",
  'measTimeStampRf' : "2021-05-12T07:43:51.652",
  'du-id' : 1003,
  'Degradation': "RSRP RSSINR"
  }

  
