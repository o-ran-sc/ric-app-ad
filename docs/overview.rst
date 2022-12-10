
Anomaly Detection Overview
==========================

Anomaly Detection (AD) is an Xapp in the Traffic Steering O-RAN use case,
which perfrom the following tasks:

#. Data will be inserted into influxDB when xApp starts. This will be removed in Future when data will be coming via KPIMON to influxDB.
#. AD, which iterates per 10 mili-second, fetches UE information from databse and send prediction to Traffic Steering
#. Traffic Steering send acknowldgement back to AD.

Expected Input
--------------

The AD Xapp expects input in following structure:

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

The AD Xapp should Detect Anomulous UE's and send those UE's information
as a JSON message via RMR with the following structure:

  {
  'ue-id' : "Waiting passenger 1",
  'measTimeStampRf' : "2021-05-12T07:43:51.652",
  'du-id' : 1003,
  'Degradation': "RSRP RSSINR"
  }
