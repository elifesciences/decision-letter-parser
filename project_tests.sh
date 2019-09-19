#!/bin/bash

tox
. .tox/py35/bin/activate
pip install coverage
pip install coveralls
COVERALLS_REPO_TOKEN=$(cat /etc/coveralls/tokens/decision-letter-parser) coveralls

