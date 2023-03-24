#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file

TOOLDIR=/home/test/tools/mythril
WORKDIR=/home/test/mythril-workspace

# Set up workdir
mkdir -p $WORKDIR
# Set up environment
mkdir -p $WORKDIR/output
mkdir -p $WORKDIR/output/bugs
touch $WORKDIR/output/log.txt
# Run mythril
$TOOLDIR/mythril/myth analyze $2 --execution-timeout $1 > \
  $WORKDIR/output/stdout.txt 2>&1
