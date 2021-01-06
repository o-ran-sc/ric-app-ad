.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2020 HCL Technologies Intellectual Property 


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
