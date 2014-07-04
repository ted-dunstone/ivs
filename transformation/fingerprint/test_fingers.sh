#!/bin/bash


echo "BEGINNING TESTS....."

echo "TEST 1"

python convert_NIST_finger.py -i TestFiles/Test1.eft  -f bmp -o Test1_new.eft

echo "TEST 2"

python convert_NIST_finger.py -i TestFiles/Test2.eft  -f bmp -o Test2_new.eft 2>&1 | grep TEST

echo "TEST 3"

python convert_NIST_finger.py -i TestFiles/Test3.eft  -f bmp -o Test3_new.eft 2>&1 | grep TEST

echo "TEST 4"

python convert_NIST_finger.py -i TestFiles/Test4.eft  -f bmp -o Test4_new.eft 2>&1 | grep TEST

echo "TEST 5"

python convert_NIST_finger.py -i TestFiles/Test5.eft  -f bmp -o Test5_new.eft 2>&1 | grep TEST

echo "TEST 6"

python convert_NIST_finger.py -i TestFiles/Test6.eft  -f bmp -o Test6_new.eft 2>&1 | grep TEST

echo "TEST 7"

python convert_NIST_finger.py -i TestFiles/Test7.eft  -f bmp -o Test7_new.eft 2>&1 | grep TEST

echo "TEST 8"

python convert_NIST_finger.py -i TestFiles/Test8.eft  -f bmp -o Test8_new.eft 2>&1 | grep TEST

echo "TEST 9"

python convert_NIST_finger.py -i TestFiles/Test9.eft  -f bmp -o Test9_new.eft 2>&1 | grep TEST

echo "TEST 10"

python convert_NIST_finger.py -i TestFiles/Test10.eft  -f bmp -o Test10_new.eft 2>&1 | grep TEST

echo "TESTING COMPLETED....."

