#!/bin/bash

echo "Running container init, use this script to install libraries etc."


pre-commit install
pip install -e .
