#!/bin/bash

# load the assessments
echo ... loading 'interests' assessment
./init_assess.py interests.txt
echo ... loading 'skills' assessment
./init_assess.py skills.txt
echo ... loading 'values' assessment
./init_assess.py values.txt
