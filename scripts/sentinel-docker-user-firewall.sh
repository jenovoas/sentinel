#!/bin/sh
set -eu

IPT=/usr/sbin/iptables
CHAIN=SENTINEL-DOCKER-USER

$IPT -w -N "$CHAIN" 2>/dev/null || true
$IPT -w -F "$CHAIN"
$IPT -w -A "$CHAIN" -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN

# Kingu is the frontend/BFF source and retains access to all published APIs.
for port in 8000 8001 5678; do
  $IPT -w -A "$CHAIN" -i wg0 -s 10.88.0.2/32 -p tcp \
    -m conntrack --ctdir ORIGINAL --ctorigdst 10.88.0.1 \
    --ctorigdstport "$port" -j RETURN
done

# Marte runs Sentinel's monitoring backend and only needs the two read APIs.
for port in 8000 8001; do
  $IPT -w -A "$CHAIN" -i wg0 -s 10.88.0.6/32 -p tcp \
    -m conntrack --ctdir ORIGINAL --ctorigdst 10.88.0.1 \
    --ctorigdstport "$port" -j RETURN
done

for port in 8000 8001 5678; do
  $IPT -w -A "$CHAIN" -p tcp \
    -m conntrack --ctdir ORIGINAL --ctorigdst 10.88.0.1 \
    --ctorigdstport "$port" -j DROP
done

# Impacta containers publish on 0.0.0.0. Keep their host ports reachable only
# from the WireGuard mesh or localhost; never from the public interface.
for port in 5435 6381 3102; do
  $IPT -w -A "$CHAIN" -i wg0 -s 10.88.0.0/24 -p tcp \
    -m conntrack --ctdir ORIGINAL --ctorigdstport "$port" -j RETURN
  $IPT -w -A "$CHAIN" -i lo -p tcp \
    -m conntrack --ctdir ORIGINAL --ctorigdstport "$port" -j RETURN
  $IPT -w -A "$CHAIN" -p tcp \
    -m conntrack --ctdir ORIGINAL --ctorigdstport "$port" -j DROP
done

$IPT -w -A "$CHAIN" -j RETURN
$IPT -w -C DOCKER-USER -j "$CHAIN" 2>/dev/null || \
  $IPT -w -I DOCKER-USER 1 -j "$CHAIN"
