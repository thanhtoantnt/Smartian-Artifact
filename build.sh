#!/bin/bash
docker build -t sochi -f Dockerfile .

# python scripts/run_experiment.py benchmarks/confuzzius_curated/reentrancy sFuzz 100 8
