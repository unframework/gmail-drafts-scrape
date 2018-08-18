#!/bin/bash -e

apt-get update -qy
DEBIAN_FRONTEND=noninteractive apt-get install -qy python3-pip

pip3 install google-api-python-client oauth2client pytz
