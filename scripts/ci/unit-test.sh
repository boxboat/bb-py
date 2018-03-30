#!/bin/bash

cd $(dirname $0)
cd ../../

set -e

pipenv run nosetests
