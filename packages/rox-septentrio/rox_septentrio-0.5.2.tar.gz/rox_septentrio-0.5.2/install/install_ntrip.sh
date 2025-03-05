#!/usr/bin/env bash

set -x
set -e

# copy ntrip client
sudo cp ntrip/ntripclient.py /usr/local/bin
sudo chmod +x /usr/local/bin/ntripclient.py
sudo cp ntrip/start_ntrip /usr/local/bin
sudo chmod +x /usr/local/bin/start_ntrip

# install service
sudo cp ntrip/ntrip.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable ntrip
sudo systemctl start ntrip
