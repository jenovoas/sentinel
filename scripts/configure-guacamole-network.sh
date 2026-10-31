#!/usr/bin/env bash
set -euo pipefail

# Alinear la política con las subredes fijadas en infrastructure/guacamole/compose.yaml.
# Aplicar runtime primero; tras el smoke, repetir con permanent. Nunca hace reload.
case "${1:-runtime}" in
  runtime) scope=() ;;
  permanent) scope=(--permanent) ;;
  *) printf 'Uso: %s [runtime|permanent]\n' "$0" >&2; exit 2 ;;
esac

internal=$(docker network inspect guacamole_internal --format '{{(index .IPAM.Config 0).Subnet}}')
egress=$(docker network inspect guacamole_ssh_egress --format '{{(index .IPAM.Config 0).Subnet}}')
[[ "$internal" == '172.27.0.0/16' && "$egress" == '172.30.0.0/16' ]] || {
  printf 'Las redes efectivas no corresponden a la configuración Guacamole. Sin cambios.\n' >&2
  exit 1
}

firewall-cmd "${scope[@]}" --zone=guac-internal --change-source=172.27.0.0/16
firewall-cmd "${scope[@]}" --zone=guac-edge --add-source=172.30.0.0/16
if firewall-cmd "${scope[@]}" --zone=guac-internal --query-source=172.25.0.0/16 >/dev/null; then
  firewall-cmd "${scope[@]}" --zone=guac-internal --remove-source=172.25.0.0/16
fi

for destination in 10.88.0.1 10.88.0.2 10.88.0.4 10.88.0.5 10.88.0.6; do
  policy=guac-to-wgmesh
  [[ "$destination" != '10.88.0.1' ]] || policy=guac-to-host
  old="rule family=ipv4 source address=172.27.0.2 destination address=$destination port port=4222 protocol=tcp accept"
  new="rule family=ipv4 source address=172.30.0.2 destination address=$destination port port=4222 protocol=tcp accept"
  firewall-cmd "${scope[@]}" --policy="$policy" --add-rich-rule="$new"
  if firewall-cmd "${scope[@]}" --policy="$policy" --query-rich-rule="$old" >/dev/null; then
    firewall-cmd "${scope[@]}" --policy="$policy" --remove-rich-rule="$old"
  fi
done
