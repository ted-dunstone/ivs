#!/bin/bash


echo "BEGINNING TESTS....."
echo "TEST 1"

python convert_NIST_finger.py -i Test1.eft  -f bmp -o Tes 

python convert_NIST_finger.py -i Test5.eft  -f bmp -o Test5_new.eft 2>&1 | grep TEST

echo "TEST 6"

python convert_NIST_finger.py -i Test6.eft  -f bmp -o Test6_new.eft 2>&1 | grep TEST

echo "TEST 7"

python convert_NIST_finger.py -i Test7.eft  -f bmp -o Test7_new.eft 2>&1 | grep TEST

echo "TEST 8"

python convert_NIST_finger.py -i Test8.eft  -f bmp -o Test8_new.eft 2>&1 | grep TEST

echo "TEST 9"

python convert_NIST_finger.py -i Test9.eft  -f bmp -o Test9_new.eft 2>&1 | grep TEST

echo "TEST 10"

python convert_NIST_finger.py -i Test10.eft  -f bmp -o Test10_new.eft 2>&1 | grep TEST

echo "TESTING COMPLETED....."

