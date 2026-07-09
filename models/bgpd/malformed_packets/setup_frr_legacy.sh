#!/bin/bash

echo "[*] Setting up FRRouting Docker Container for Parity Testing..."

# Stop and remove existing container if it exists
docker stop frr-lab 2>/dev/null
docker rm frr-lab 2>/dev/null

# Start FRR container with port mapping
docker run -d --privileged --name frr-lab -p 1179:179 frrouting/frr:v7.5.0

echo "[*] Waiting for container to initialize..."
sleep 3

# Enable bgpd
docker exec frr-lab sed -i 's/bgpd=no/bgpd=yes/g' /etc/frr/daemons

# Create minimal FRR config
cat << 'EOF' > frr.conf.tmp
log file /tmp/bgpd.log debugging
router bgp 65001
 no bgp ebgp-requires-policy
 neighbor FUZZ peer-group
 neighbor FUZZ remote-as 65002
 bgp listen range 0.0.0.0/0 peer-group FUZZ
EOF

docker cp frr.conf.tmp frr-lab:/etc/frr/frr.conf
rm frr.conf.tmp

# Restart FRR container to apply daemons and config changes
docker restart frr-lab
echo "[*] Waiting for bgpd to start..."
sleep 3

# Verify
if docker exec frr-lab ps aux | grep -q bgpd; then
    echo "[+] FRR Container setup complete! bgpd is running and listening on localhost:1179"
else
    echo "[-] Failed to start bgpd in container. Check logs."
    exit 1
fi
