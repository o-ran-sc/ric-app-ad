# ==================================================================================
#  Copyright (c) 2020 HCL Technologies Limited.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ==================================================================================



Developers Guide
=================

.. contents::
   :depth: 3
   :local:


Version bumping the Xapp
------------------------

This project follows semver. When changes are made, update the version strings in:

#. ``container-tag.yaml``
#. ``docs/release-notes.rst``
#. ``setup.py``
#. ``xapp-descriptor/config.json``


Testing RMR Healthcheck
-----------------------
The following instructions should deploy the AD container in bare docker, and allow you
to test that the RMR healthcheck is working.

::

    docker build -t ad:latest -f  Dockerfile .
    docker run -d --net=host -e USE_FAKE_SDL=1 ad:latest
    docker exec -it CONTAINER_ID /usr/local/bin/rmr_probe -h 127.0.0.1:4560


Unit Testing
------------

Running the unit tests requires the python packages ``tox`` and ``pytest``.

The RMR library is also required during unit tests. If running directly from tox
(outside a Docker container), install RMR according to its instructions.

Upon completion, view the test coverage like this:

::

   tox
   open htmlcov/index.html

Alternatively, if you cannot install RMR locally, you can run the unit
tests in Docker. This is somewhat less nice because you don't get the
pretty HTML report on coverage.

::

   docker build  --no-cache -f Dockerfile-Unit-Test .
