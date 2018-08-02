#!/bin/bash

cd $(dirname $0)
cd ../../test/functional

set -e

pipenv run nosetests
