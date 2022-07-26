#!/bin/bash
set -e
. install.sh
source venv/bin/activate
coverage run -m pytest tests
