#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file

TOOLDIR=/home/test/tools/mythril
WORKDIR=/home/test/mythril-workspace

FILENAME="$2"
VERSION=$(python3 /home/test/scripts/get_solc_version.py "$FILENAME")
solc-select install $VERSION
solc-select use $VERSION

# Set up workdir
mkdir -p $WORKDIR
# Set up environment
mkdir -p $WORKDIR/output
mkdir -p $WORKDIR/output/bugs
touch $WORKDIR/output/log.txt
# Run mythril
$TOOLDIR/mythril/myth analyze $2 --solv $VERSION --execution-timeout $1  -o json > \
  $WORKDIR/output/stdout.txt 2>&1

cp -r $WORKDIR/output/ /home/test/
