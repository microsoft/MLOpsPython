#!/bin/sh
set -eux
flake8 --output-file=lint-testresults.xml --format junit-xml
python -m pytest tests/unit --cov=diabetes_regression --cov-report=html --cov-report=xml --junitxml=unit-testresults.xml
