#!/bin/bash

protoc --python_out=../protobuf/   ./*.proto --proto_path=.
