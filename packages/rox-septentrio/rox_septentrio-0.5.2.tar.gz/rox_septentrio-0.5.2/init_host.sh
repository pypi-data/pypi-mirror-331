#!/bin/bash


DEV_IMG=local/septentrio-gps

mkdir -p /var/tmp/container-extensions

# build docker image
docker build -t $DEV_IMG --build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g) -f .devcontainer/Dockerfile .
