#!/bin/bash
protoc -I=. --python_out=. protocol.proto 
./clear.py 
./newpost.py --test
