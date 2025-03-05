#!/bin/bash

# Start socat in the background
socat -d pty,rawer,b115200,echo=0,link=/tty/tty_nmea_rx \
      pty,rawer,b115200,echo=0,link=/tty/tty_nmea_tx &

# Execute the Docker container's original CMD
exec "$@"
