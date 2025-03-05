#!/usr/bin/env bash

# install system packages
sudo apt-get update && sudo apt-get install -y socat picocom

sudo cp 80-septentrio.rules /etc/udev/rules.d
sudo chown root:root /etc/udev/rules.d
sudo udevadm control --reload
