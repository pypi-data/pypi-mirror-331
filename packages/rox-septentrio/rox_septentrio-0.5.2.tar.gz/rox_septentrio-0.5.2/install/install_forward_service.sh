#!/bin/bash

# Check if the service file already exists
if [[ -e /etc/systemd/system/a_forward-gps.service ]]; then
    echo "The service file already exists. Exiting."
    exit 0
fi

# Create the executable script file
cat << 'EOF' > /usr/local/bin/a_forward-gps.sh
#!/bin/bash
socat tcp-listen:9000,reuseaddr,fork tcp:192.168.3.1:80
EOF

# Make the script executable
chmod +x /usr/local/bin/a_forward-gps.sh

# Create the systemd service file
cat << 'EOF' > /etc/systemd/system/a_forward-gps.service
[Unit]
Description=Forward GPS Port

[Service]
ExecStart=/usr/local/bin/a_forward-gps.sh

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to recognize the new service
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable a_forward-gps.service

# Start the service immediately
systemctl start a_forward-gps.service
