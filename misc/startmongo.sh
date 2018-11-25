#!/bin/bash

echo "Starting mongod..."

cd $(dirname $0)
mkdir -p ../.db/ 2>/dev/null

mongod --dbpath ../.db/

