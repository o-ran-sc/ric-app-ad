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
For AD xapp we require ueMeasReport(UE related dataset)

AD xApp expect UE data from influxDB database in following structure:
	* There exists database with name "UEData"
	* Inside "UEData" database we have three measurments namely "liveUE", "train", "valid"
	
Note: *We need to specify influxdb service ruuning in RIC platform in database.py(host = <service name>.<namespace>)
	  *InfluxDB will be populated when xApp starts via insert.py. This will be depreciated in next release when there will be data coming from KPIMON
	
Need to update this file each time when there is any modifications in the following components. 

main.py: 
* Initiates xapp api, populated influxDB with data and runs the entry() using xapp.run()
* If Model is not present in the current path, run train() to train the model for the prediction.
* Call predict function to perform the following activities for every 10 milisecond. 
   a) Currently read the input from "liveUE" measurments and iterate through it. (Needs to update: To iterate every 10 miliseconds and fetch latest sample from influxDB) 
   b) Detect anomalous records for the inputs
   c) send the UEID, DU-ID, Degradation type and timestamp for the anomalous records to the Traffic Steering (via rmr with the message type as 30003)
   d) Get the acknowledgement message from the traffic steering 

Note: Need to implement the logic if we do not get the acknowledgment from the TS. (How xapp api handle this?)

ad_train.py - Fetch "train" and "valid"(labelled dataset) measurments from influxDB for build and testing Isolation Forest model. Save final model. 
			  
	Model: Model has been trained using history data feteched from influxdb for all UE's 
	validation: we need to have smaller sample dataset(labelled) for validation in influxDB for model validation.

processing.py:
It performs the following activities:
* Columns that are not useful for the prediction will be dropped(UEID, Category, & Timestamp)
* Filetered numeric data type(as per problem need)
* verify and drop the highly correlated parameters
* Use Transformation for makine all parameters in same scale and saved transformer info.
* returns remaining parameters required for training and testing


ad_model.py: 
* Call Predict method to get the anomalous users and send information related to anomalous user to Traffic steering xapp

database.py
* This module creates connection to influxDB and have methods to read and write data into influxDB


