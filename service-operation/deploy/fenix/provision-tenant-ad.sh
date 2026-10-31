#!/usr/bin/env bash
# Provisiona la estructura AD de un tenant/proyecto en el dominio.
# Uso: provision-tenant-ad.sh <tenant-id> [--admin <usuario>]... [--project <project-id>]... [--n8n] [--n8n-user <usuario>]...
# Idempotente: crea OU/grupos solo si faltan y agrega los admins indicados.
set -euo pipefail
umask 077

BASE_DN="DC=pinguinoseguro,DC=cl"
TENANTS_DN="OU=Tenants,${BASE_DN}"

usage() {
  cat >&2 <<EOF
Uso: $0 <tenant-id> [--admin <usuario>]... [--project <project-id>]... [--n8n] [--n8n-user <usuario>]...
Crea/verifica:
  OU=<tenant-id>,OU=Tenants,DC=pinguinoseguro,DC=cl
  SP-Tenant-<tenant-id>-Users
  SP-Tenant-<tenant-id>-Admins
  SP-Tenant-<tenant-id>-Technicians
  SP-Project-<tenant-id>-<project-id>-Users
  SP-N8N-Flows (con --n8n o --n8n-user)
EOF
  exit 1
}

[ "$#" -ge 1 ] || usage
TENANT_ID="$1"
shift
[[ "$TENANT_ID" =~ ^[a-z0-9][a-z0-9._-]{0,47}$ ]] || {
  echo "tenant-id inválido: minúsculas, 1-48 caracteres [a-z0-9._-]" >&2
  exit 1
}

ADMINS=()
PROJECTS=()
N8N=false
N8N_USERS=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --admin)
      [ "$#" -ge 2 ] || usage
      ADMINS+=("$2")
      shift 2
      ;;
    --project)
      [ "$#" -ge 2 ] || usage
      PROJECTS+=("$2")
      shift 2
      ;;
    --n8n)
      N8N=true
      shift
      ;;
    --n8n-user)
      [ "$#" -ge 2 ] || usage
      N8N_USERS+=("$2")
      N8N=true
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

for user in "${ADMINS[@]}" "${N8N_USERS[@]}"; do
  if ! samba-tool user show "$user" >/dev/null 2>&1; then
    echo "Usuario AD inexistente: $user" >&2
    exit 1
  fi
done

TENANT_OU_DN="OU=${TENANT_ID},${TENANTS_DN}"
TENANT_OU_REL="OU=${TENANT_ID},OU=Tenants"

ensure_ou() {
  local dn="$1" rel="$2" description="$3"
  if samba-tool ou list 2>/dev/null | grep -Fxq "$rel"; then
    echo "OU existe: $dn"
  else
    samba-tool ou create "$dn" --description="$description" >/dev/null
    echo "OU creada: $dn"
  fi
}

ensure_group() {
  local name="$1" description="$2"
  if samba-tool group list 2>/dev/null | grep -Fxq "$name"; then
    echo "Grupo existe: $name"
  else
    samba-tool group add "$name" \
      --group-type=Security \
      --group-scope=Global \
      --groupou="$TENANT_OU_REL" \
      --description="$description" >/dev/null
    echo "Grupo creado: $name"
  fi
}

add_members() {
  local group="$1"
  shift
  [ "$#" -gt 0 ] || return 0
  samba-tool group addmembers "$group" "$(IFS=,; echo "$*")"
}

ensure_ou "$TENANT_OU_DN" "$TENANT_OU_REL" "Tenant ${TENANT_ID} — SecurePenguin"

USERS_GROUP="SP-Tenant-${TENANT_ID}-Users"
ADMINS_GROUP="SP-Tenant-${TENANT_ID}-Admins"
TECHS_GROUP="SP-Tenant-${TENANT_ID}-Technicians"

ensure_group "$USERS_GROUP" "Usuarios del tenant ${TENANT_ID}"
ensure_group "$ADMINS_GROUP" "Administradores del tenant ${TENANT_ID}"
ensure_group "$TECHS_GROUP" "Técnicos del tenant ${TENANT_ID}"

if [ "${#ADMINS[@]}" -gt 0 ]; then
  add_members "$ADMINS_GROUP" "${ADMINS[@]}"
  add_members "$USERS_GROUP" "${ADMINS[@]}"
fi

if [ "$N8N" = true ]; then
  if ! samba-tool group list 2>/dev/null | grep -Fxq "SP-N8N-Flows"; then
    echo "Grupo SP-N8N-Flows no existe" >&2
    exit 1
  fi
  N8N_MEMBERS=("${ADMINS[@]}" "${N8N_USERS[@]}")
  if [ "${#N8N_MEMBERS[@]}" -gt 0 ]; then
    add_members "SP-N8N-Flows" "${N8N_MEMBERS[@]}"
  fi
fi

for project in "${PROJECTS[@]}"; do
  [[ "$project" =~ ^[a-z0-9][a-z0-9._-]{0,19}$ ]] || {
    echo "project-id inválido: minúsculas, 1-20 caracteres [a-z0-9._-]" >&2
    exit 1
  }
  name="SP-Project-${TENANT_ID}-${project}-Users"
  if [ "${#name}" -gt 64 ]; then
    echo "Nombre de grupo demasiado largo para AD CN: $name" >&2
    exit 1
  fi
  ensure_group "$name" "Usuarios del proyecto ${project} del tenant ${TENANT_ID}"
done

echo "tenant_ou=${TENANT_OU_DN}"
echo "groups=${USERS_GROUP},${ADMINS_GROUP},${TECHS_GROUP}"
