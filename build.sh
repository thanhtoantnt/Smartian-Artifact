#!/bin/bash
docker build -t sochi -f Dockerfile .

# python scripts/run_experiment.py B1 sFuzz 36
