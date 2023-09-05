#! /bin/sh

nl="\n-------------------------------------\n";

# First 24 bits of the assigned Docker network
DOCKER_NET_24=$( ip route show default | awk '{ print $3 }' | cut -d . -f 1-3 )

# Check IP subnet for container:
if [[ -z "${IP_WG_ENV}" ]]; then
     IP_WG_ENV=${DOCKER_NET_24}.0/16
#    IP_WG_ENV=10.0.0.0/24;
fi

# Setup boringtun interface and start
if [[ -f /data/boringtun ]]; then
    printf "Starting Wireguard userspace (boringtun)\n";
    mkdir -p /dev/net;
    mknod /dev/net/tun c 10 200;
    /data/boringtun -f wg0 & # Sends logs to STDOUT
    wireguard_pid=$!;
else
    printf "WARNING: Wireguard binary not found. This container will not run\n";
    exit 1;
fi

# Add a sleep for any Wireguard intialization slowness
while [[ $(wg show wg0 2>&1) == *"Protocol not supported"  ]]; do
	printf "Startup error: protocol not supported: sleeping...\n";
    sleep 1;
done

# Extract containers default gateway interface (usually eth0)
read _ _ _ _ iface < <(ip route show default);

# This sets the IPv4 VPN network on the server side. Can be changed by env var.
printf "Setting ipv4 network address options... $(ip addr add $IP_WG_ENV dev wg0)\n";

# NOTE: may want to turn of IP MASQ when this goes live or people may actually use this as VPN
# First delete the rule (this avoids adding the rule every time the container restarts - also errors out gracefully)
printf "Deleting rules (if they exist)...\n" && iptables-legacy -D FORWARD -i wg0 -j ACCEPT && iptables-legacy -D FORWARD -i $iface -j ACCEPT && iptables-legacy -t nat -D POSTROUTING -o $iface -j MASQUERADE;
printf "Configuring iptables-legacy...\n" && iptables-legacy -A FORWARD -i wg0 -j ACCEPT && iptables-legacy -A FORWARD -i $iface -j ACCEPT && iptables-legacy -t nat -A POSTROUTING -o $iface -j MASQUERADE;

if [[ -f /config/iptables.sh ]]; then
    source /config/iptables.sh;
fi

# Set MTU lower than the default 1500 accounting for wg overhead
printf "Setting network interface mtu... $(ip link set mtu 1420 qlen 1000 dev wg0)\n";

# Create a new server/client configuration
/data/genconfs.sh ${DOCKER_NET_24}

# Set wireguard configuration
if [[ -f /config/wireguard.conf ]]; then
    printf "${nl}Setting config... $(wg setconf wg0 /config/wireguard.conf)\n";
else
    printf "WARNING: /config/wireguard.conf file is missing. This container cannot start\n";
    exit 1;
fi

# This brings up the wireguard interface inside the container
printf "Bringing interface up... $(ip link set wg0 up)${nl}";

printf "Configuring routing for packets destined for VPN client..." 
route add ${DOCKER_NET_24}.37 dev wg0

# Display the running configs
printf "${nl}Active network interfaces:\n$(ip addr 2>&1)";
printf "${nl}Active network ipv4 route table:\n$(ip -4 route)";
printf "${nl}iptables-legacy ipv4 config:\n$(iptables-legacy -t nat -L)";
printf "${nl}Active Wireguard config:\n$(wg show wg0 2>&1)";

# Test ping to Google for connectivity validation
printf "${nl}IPv4 connectivity validation:\n" && /bin/ping -4 -q -c 1 ipv4.google.com;
printf "${nl}Running....\n"

wait -n;
printf "${nl}WARNING: Process terminated, restarting...${nl}";
exit 0;
