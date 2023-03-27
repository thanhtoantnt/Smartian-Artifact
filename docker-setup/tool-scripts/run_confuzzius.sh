#!/bin/bash

# Arg1 : Time limit
# Arg2 : Source file

TOOLDIR=/home/test/tools/confuzzius
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

python3 $TOOLDIR/ConFuzzius/fuzzer/main.py -s $2 --solc "v$VERSION" --evm byzantium -t $1 > \
                      $WORKDIR/output/stdout.txt 2>&1

cp -r $WORKDIR/output/ /home/test/
