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
Need to update this file each time when there is any modifications in the following components. 

main.py: 
* Initiates xapp api and runs the entry() using xapp.run()
* If RF model is not present in the path, run train() to train the model for the prediction.
  Call predict function for every 1 second(for now as we are using simulated data).
* Read the input csv file that has both normal and anomalous data.
* Simulate diff UEIDs that participate in the anomaly by randomly selecting records from this scoring data set
* Send the UEID and timestamp for the anomalous entries to the Traffic Steering (rmr with the message type as 30003)
* Get the acknowledgement message from the traffic steering.

ad_train.py - Read all the csv files in the current path and create trained model(RF)

processing.py:
It performs the following activities:
* Columns that are not useful for the prediction will be dropped(UEID, Category, & Timestamp)
* Convert integer and float type into numeric data type.
* verify and drop the highly correlated parameters.
* returns UEID, timestamp and category for the anamolous entries.

ad_model.py: 
* Extract all the unique UEID and filters only the randomly selected UEID(this step will be removed when we implement in sdl way of getting the UEID).
* Call Predict method to get the final data for the randomly selected UEID.

tb_format.py:
* start the preprocessing, processing steps using the keycolumns
* populate current timestamp value for MeasTimestampRF

