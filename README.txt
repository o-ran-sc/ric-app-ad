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

Usage of all the programs and files have been mentioned below for the reference.
For AD xapp we require UEReport (UE related dataset)

AD xApp expect UE data from influxDB database in following structure:
	* There exists database with name "RIC-Test"
	* Inside "RIC-Test" database we have measurments namely "UEReports"
	
Note: *We need to update ad_config.ini with influxdb configuration. 
Update host as one of the following:
	1. influxdb service ruuning in RIC platform (host = <service name>.<namespace>) 
	   OR IP of influxdb pod
	2. Update user and password for influxDB instance

To polpulate influxdb with static data provided in .csv (ue.csv). 
	1. Run "python3 insert.py"
	2. Wait for few minutes before deploying AD xApp
	Note: This will be depreciated in next release when there will be data coming from KPIMON
	

AD xApp performs following:

* Initiates xapp api, make connection with influxDB and runs the entry() using xapp.run()
* If Model is not present in the current path, 
   a) Read history data from InfluxDB
   b) apply pre-processing steps
   c) trigger Training of ML model.
   d) after model validation, save transformation, model artifacts
* Detect anomalous user in real-time. 
   a) Read live data from influxDB every 0.5 second
   b) Detect anomalous records on given input
   c) Investigate degradation type for anomalous users
* Listens to RMR port for A1 policy (message type 20011) in a format given below. Which consists throughput threshold parameter (default: 70%) for an degradataion event to qualify for a handover
   {'operation': 'CREATE', 'payload': '{\"thp_threshold\":74}', 'policy_instance_id': 'demo-1', 'policy_type_id': '9997'}"}
* Send the ue-id, DU-ID, Degradation type and timestamp for the qualified anomalous records to the Traffic Steering (via rmr with the message type as 30003)
* Get the acknowledgement message from the traffic steering 
* store xApp result in "AD" measurement of influxDB

Note: Need to implement the logic if we do not get the acknowledgment from the TS. (How xapp api handle this?)
