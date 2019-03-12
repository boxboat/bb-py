#!/bin/bash

cd $(dirname $0)
cd ../../

set -e
apt-get upgrade && apt-get install -y python3-dev
pipenv sync --dev
