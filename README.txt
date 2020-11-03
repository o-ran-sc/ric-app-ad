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
* If hdbscan is not present in the current path, run train() to train the model for the prediction.
* Call predict function to perform the following activities for every 1 second. 
   a) Read the input csv file( 1000 UEID samples)
   b) Predict the anomaly records for the randomly selected UEID
   c) send the UEID and timestamp for the anomalous entries to the Traffic Steering (rmr with the message type as 30003)
   d) Get the acknowledgement message from the traffic steering.

Note: Need to handle the logic if we do not get the acknowledgment from the TS.
      How xapp api handle this logic

ad_train.py - train hdbscan model using the input csv files and save the model. 

dbscan: Model has been trained using the train dataset(train sampling for prediction)

ue_test.csv: Input csv file has 1000 samples and for each UEID has one or more than one entries for poor signal.

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

