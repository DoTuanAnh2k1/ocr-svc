#!/bin/bash
for i in {1..5}
do
   if [[ "$1" = 'seq' ]]; then
      echo "Test: $i - $(python client/main.py ./client/test.jpg | grep 'Processing time')"
   else
      python client/main.py ./client/test.jpg >> tmp.log &
   fi
done
