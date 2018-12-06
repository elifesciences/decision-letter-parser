#!/bin/bash
set -e # everything must succeed.
pip install -r requirements.txt
pip install tox
pip install coveralls
tox