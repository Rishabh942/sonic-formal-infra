#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[*] Setting up FRRouting Docker Container for Parity Testing..."

# Stop and remove existing container if it exists
docker stop frr-lab 2>/dev/null || true
docker rm frr-lab 2>/dev/null || true

# Start FRR container with port mapping
docker run -d --privileged --name frr-lab -p 127.0.0.1:1179:179 quay.io/frrouting/frr:10.0.1

echo "[*] Waiting for container to initialize..."
sleep 3

# Enable bgpd
docker exec frr-lab sed -i 's/bgpd=no/bgpd=yes/g' /etc/frr/daemons

# Create minimal FRR config
cat << 'EOF' > frr.conf.tmp
log file /tmp/bgpd.log debugging
 router bgp 65001
  no bgp ebgp-requires-policy
  bgp graceful-restart
  neighbor FUZZ peer-group
  neighbor FUZZ remote-as 65002
  neighbor FUZZ disable-connected-check
  neighbor FUZZ ebgp-multihop 255
  bgp listen range 0.0.0.0/0 peer-group FUZZ

  neighbor 127.0.0.1 peer-group FUZZ
  neighbor 127.0.0.1 remote-as 65003
  neighbor 127.0.0.1 port 1790
  neighbor 127.0.0.1 timers 3 9

EOF

docker cp frr.conf.tmp frr-lab:/etc/frr/frr.conf
docker cp "$SCRIPT_DIR/dummy_peer.py" frr-lab:/frr/dummy_peer.py
rm frr.conf.tmp

# Restart FRR container to apply daemons and config changes
docker restart frr-lab
sleep 2
docker exec -d frr-lab python3 /frr/dummy_peer.py
echo "[*] Waiting for bgpd to start..."
sleep 3

# Verify
if docker exec frr-lab ps aux | grep -q bgpd; then
    echo "[+] FRR Container setup complete! bgpd is running and listening on localhost:1179"
else
    echo "[-] Failed to start bgpd in container. Check logs."
    exit 1
fi
