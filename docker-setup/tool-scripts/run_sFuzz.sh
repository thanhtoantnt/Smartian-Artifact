#!/bin/bash


# Arg1 : Time limit
# Arg2 : Source file

TOOLDIR=/home/test/tools/sFuzz
WORKDIR=/home/test/sFuzz-workspace

FILENAME="$2"

VERSION=$(python3 /home/test/scripts/get_solc_version.py "$FILENAME")

solc-select install $VERSION
solc-select use $VERSION

CONTRACTS=$(python3 /home/test/scripts/printContractNames.py "$FILENAME")

# Set up workdir
mkdir -p $WORKDIR
# Set up fuzzer
cp $TOOLDIR/fuzzer $WORKDIR/fuzzer
# Set up environment
cp -r $TOOLDIR/sFuzz/assets $WORKDIR
mkdir -p $WORKDIR/output
mkdir -p $WORKDIR/contracts
for CONTRACT in $CONTRACTS; do
    cp "$FILENAME" $WORKDIR"/contracts/$CONTRACT.sol"
done

touch $WORKDIR/output/log.txt
# Run sFuzz
cd $WORKDIR
./fuzzer -g -r 0 -d $1 --attacker ReentrancyAttacker > $WORKDIR/output/stdout.txt 2>&1
chmod +x ./fuzzMe
./fuzzMe >> $WORKDIR/output/stdout.txt 2>&1
cp -r $WORKDIR/output/ /home/test/
