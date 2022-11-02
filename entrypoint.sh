#!/usr/bin/env bash

# Start sshd
echo "Starting ssh server..."
service ssh restart

# Connect to AWS VPN
echo "Connecting to VPN..."
openvpn --config ../challenge_data/aws-cvpn-config.ovpn --daemon

# Mount shared drive
echo "Mounting shared drive..."
mount -t nfs 10.0.137.113:/fsx/ ../challenge_data/aws

# Config broker
echo "Configuring broker..."
pdm run suam-config install --no-symlink --input=../challenge_data/data/broker.conf.yaml

bash