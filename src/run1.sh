#!/bin/bash

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")
echo $BASEDIR
cd $BASEDIR

sh build.sh
cd bin
time ./CodeCraft-2021 <../../data/Finall/training-1.txt >../../data/Finall/answer1.txt
time ./CodeCraft-2021 <../../data/Finall/training-2.txt >../../data/Finall/answer2.txt
cd ../../data/Finall
python judge.py
# time ./CodeCraft-2021 < ../../data/training-1.txt
