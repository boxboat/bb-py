#!/bin/bash

cd $(dirname $0)
cd ../../test/unit

set -e

pipenv run nosetests
