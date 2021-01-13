# ==================================================================================
#  Copyright (c) 2019 AT&T Intellectual Property.
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
FROM frolvlad/alpine-miniconda3
# RMR setup
RUN mkdir -p /opt/route/

# copy rmr files from builder image in lieu of an Alpine package
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/lib64/librmr* /usr/local/lib64/

COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/bin/rmr* /usr/local/bin/
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
COPY local.rt /opt/route/local.rt
ENV RMR_SEED_RT /opt/route/local.rt

RUN apk update && apk add gcc musl-dev
RUN pip install ricxappframe
RUN conda update -n base -c defaults conda
RUN conda install pandas
RUN conda install -c conda-forge/label/cf202003 hdbscan
RUN pip install schedule

COPY ad/ /tmp/ad
ENV PYTHONUNBUFFERED 1
CMD python /tmp/ad/main.py

