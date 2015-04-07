#!/bin/bash
protoc -I=. --python_out=. protocol.proto 