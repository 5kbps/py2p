#!/bin/bash
protoc -I=. --python_out=. protocol.proto 
protoc -I=. --python_out=. key_exchange.proto 
./clear.py 
./newpost.py --test
