#!/bin/bash
# Install dependencies for Lambda layer
cd python
pip install -r requirements.txt -t .
cd .. 