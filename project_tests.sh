#!/bin/bash

pip install coveralls
tox
. .tox/py35/bin/activate
COVERALLS_REPO_TOKEN=$(cat /etc/coveralls/tokens/decision-letter-parser) coveralls

