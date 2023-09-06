#!/bin/bash

SERVER_PRIVATE_KEY=`wg genkey`
SERVER_PUBLIC_KEY=`echo ${SERVER_PRIVATE_KEY} | wg pubkey`
CLIENT_PRIVATE_KEY=`wg genkey`
CLIENT_PUBLIC_KEY=`echo ${CLIENT_PRIVATE_KEY} | wg pubkey`

mkdir -p /config

echo "Saving server configuration in /config/wireguard.conf"

cat <<EOF > /config/wireguard.conf
[Interface]
ListenPort = 51820
PrivateKey = ${SERVER_PRIVATE_KEY}

[Peer]
PublicKey = ${CLIENT_PUBLIC_KEY}
AllowedIPs = ${1}.37/32
EOF

echo "Outputing client configuration to screen"

echo "<ClientConfig>"
cat <<EOF
[Interface]
PrivateKey = ${CLIENT_PRIVATE_KEY}
ListenPort = 51820
Address = ${1}.37/16

[Peer]
PublicKey = ${SERVER_PUBLIC_KEY}
AllowedIPs = 0.0.0.0/0, ::/0
EOF
echo "</ClientConfig>"
