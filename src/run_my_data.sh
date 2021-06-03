#!/bin/bash
# sh build.sh

cd bin

echo "***************** generate-data 1 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-generate-1.txt > ../../data/Rematch/generate-data/answer1.txt
echo "***************** generate-data 2 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-generate-2.txt > ../../data/Rematch/generate-data/answer2.txt
echo "***************** generate-data 3 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-generate-3.txt > ../../data/Rematch/generate-data/answer3.txt
echo "***************** generate-data 4 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-generate-4.txt > ../../data/Rematch/generate-data/answer4.txt
echo "***************** generate-data 5 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-generate-5.txt > ../../data/Rematch/generate-data/answer5.txt
echo "***************** training-swap 6 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-swap-1.txt > ../../data/Rematch/generate-data/answer6.txt
echo "***************** training-swap 7 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-swap-2.txt > ../../data/Rematch/generate-data/answer7.txt
echo "***************** training-random 8 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-random-1.txt > ../../data/Rematch/generate-data/answer8.txt
echo "***************** training-random 9 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-random-2.txt > ../../data/Rematch/generate-data/answer9.txt
echo "***************** training-random 10 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-random-3.txt > ../../data/Rematch/generate-data/answer10.txt
echo "***************** training-random 11 *****************"
time ./CodeCraft-2021 < ../../data/Rematch/generate-data/training-random-4.txt > ../../data/Rematch/generate-data/answer11.txt
echo "***************** score *****************"


cd ../../data/Rematch/generate-data
python judge.py


:<<!
'''
IOT
***************** generate-data 1 *****************

real    0m26.302s
user    0m0.000s
sys     0m0.015s
***************** generate-data 2 *****************

real    0m2.829s
user    0m0.000s
sys     0m0.000s
***************** generate-data 3 *****************

real    0m13.961s
user    0m0.000s
sys     0m0.016s
***************** generate-data 4 *****************

real    0m10.699s
user    0m0.000s
sys     0m0.015s
***************** generate-data 5 *****************

real    0m13.281s
user    0m0.000s
sys     0m0.015s
***************** score *****************
training-generate  1
total hardware_cost:  900154921
total energy_cost:  719732717
total cost:  1619887638
total migration times:  67687
total purchase kind_nums:  6
total purchase nums:  15651
------------------------------

training-generate  2
total hardware_cost:  698982044
total energy_cost:  42403481
total cost:  741385525
total migration times:  14282
total purchase kind_nums:  7
total purchase nums:  12322
------------------------------

training-generate  3
total hardware_cost:  1732121326
total energy_cost:  191860635
total cost:  1923981961
total migration times:  30469
total purchase kind_nums:  5
total purchase nums:  28787
------------------------------

training-generate  4
total hardware_cost:  496269682
total energy_cost:  502783275
total cost:  999052957
total migration times:  152307
total purchase kind_nums:  18
total purchase nums:  7363
------------------------------

training-generate  5
total hardware_cost:  918602255
total energy_cost:  523762977
total cost:  1442365232
total migration times:  64360
total purchase kind_nums:  8
total purchase nums:  15702
------------------------------

training all:  6726673313
'''
!