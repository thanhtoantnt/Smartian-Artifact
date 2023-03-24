#!/bin/bash
docker build -t sochi -f Dockerfile .

# python run_sfuzz_experiment.py benchmarks/confuzzius_curated/reentrancy/ 10 8
