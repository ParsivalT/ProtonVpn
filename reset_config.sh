#!/bin/bash

if [ "$EUID" -ne 0 ];then
  echo "Necessario executar como ROOT"
  exit 1
fi

# Stop openvpn services
pkill openvpn


# Restart config Network
systemctl restart NetworkManager

# Restart dnscrypt-proxy
systemctl restart dnscrypt-proxy
