#!/usr/bin/env python3
"""Idempotently assign the Fenix mail identities to their AD access group."""

from __future__ import annotations

import socket
import sys

import ldb
from samba.auth import system_session
from samba.param import LoadParm
from samba.samdb import SamDB


DOMAIN_DN = "DC=pinguinoseguro,DC=cl"
MAIL_GROUP_DN = f"CN=Mail-Users,CN=Users,{DOMAIN_DN}"
SERVICE_BIND_DN = f"CN=svc-dovecot-bind,OU=ServiceAccounts,{DOMAIN_DN}"
NON_EXPIRING_SERVICE_ACCOUNTS = {
    "svc-dovecot-bind": SERVICE_BIND_DN,
    "n8n": f"CN=n8n,OU=MailUsers,{DOMAIN_DN}",
    "monitoreo": f"CN=monitoreo,OU=MailUsers,{DOMAIN_DN}",
}
ALIASES = {
    "admin": ["admin@www.pinguinoseguro.cl"],
    "contacto": ["contacto@www.pinguinoseguro.cl"],
    "info": ["info@www.pinguinoseguro.cl"],
    "jnovoas": [
        "jnovoas@www.pinguinoseguro.cl",
        "jaime@pinguinoseguro.cl",
        "jaime@www.pinguinoseguro.cl",
    ],
    "max": ["max@www.pinguinoseguro.cl"],
    "monitoreo": ["monitoreo@www.pinguinoseguro.cl"],
    "n8n": ["n8n@www.pinguinoseguro.cl"],
    "scliente": [],
    "ventas": [],
}


def text_value(value) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def one_entry(db: SamDB, dn: str):
    entries = db.search(base=dn, scope=ldb.SCOPE_BASE)
    if len(entries) != 1:
        raise RuntimeError(f"Expected one AD object at {dn}; got {len(entries)}")
    return entries[0]


def add_member(db: SamDB, group_dn: str, member_dn: str) -> bool:
    group = one_entry(db, group_dn)
    current = {text_value(value).lower() for value in group.get("member", [])}
    if member_dn.lower() in current:
        return False
    msg = ldb.Message()
    msg.dn = ldb.Dn(db, group_dn)
    msg["member"] = ldb.MessageElement(
        [member_dn], ldb.FLAG_MOD_ADD, "member"
    )
    db.modify(msg)
    return True


def add_addresses(db: SamDB, account: str, addresses: list[str]) -> int:
    dn = f"CN={account},OU=MailUsers,{DOMAIN_DN}"
    if account == "jnovoas":
        dn = f"CN=jnovoas,CN=Users,{DOMAIN_DN}"
    entry = one_entry(db, dn)
    current = {
        text_value(value).lower() for value in entry.get("proxyAddresses", [])
    }
    values = [f"smtp:{address}" for address in addresses]
    canonical = f"SMTP:{account}@pinguinoseguro.cl"
    if canonical.lower() not in current:
        values.append(canonical)
    missing = [value for value in values if value.lower() not in current]
    if not missing:
        return 0
    msg = ldb.Message()
    msg.dn = ldb.Dn(db, dn)
    msg["proxyAddresses"] = ldb.MessageElement(
        missing, ldb.FLAG_MOD_ADD, "proxyAddresses"
    )
    db.modify(msg)
    return len(missing)


def disable_password_expiry(db: SamDB, account_dn: str) -> bool:
    account = one_entry(db, account_dn)
    current_uac = int(text_value(account.get("userAccountControl", [b"0"])[0]))
    no_expiry_flag = 0x10000
    if current_uac & 0x2:
        raise RuntimeError(f"Service account is disabled: {account_dn}")
    if current_uac & no_expiry_flag:
        return False
    msg = ldb.Message()
    msg.dn = ldb.Dn(db, account_dn)
    msg["userAccountControl"] = ldb.MessageElement(
        [str(current_uac | no_expiry_flag)],
        ldb.FLAG_MOD_REPLACE,
        "userAccountControl",
    )
    db.modify(msg)
    return True


def main() -> int:
    if socket.gethostname().split(".")[0].lower() != "fenix":
        raise RuntimeError("Run this directory update only on the Fenix PDC")

    lp = LoadParm()
    lp.load("/etc/samba/smb.conf")
    db = SamDB(
        url="/var/lib/samba/private/sam.ldb",
        session_info=system_session(),
        lp=lp,
    )
    if str(db.domain_dn()).lower() != DOMAIN_DN.lower():
        raise RuntimeError(f"Unexpected Samba domain: {db.domain_dn()}")

    group = one_entry(db, MAIL_GROUP_DN)
    _ = group
    membership_changes = 0
    alias_changes = 0
    for account, aliases in ALIASES.items():
        dn = f"CN={account},OU=MailUsers,{DOMAIN_DN}"
        if account == "jnovoas":
            dn = f"CN=jnovoas,CN=Users,{DOMAIN_DN}"
        one_entry(db, dn)
        membership_changes += add_member(db, MAIL_GROUP_DN, dn)
        alias_changes += add_addresses(db, account, aliases)

    expiry_changes = sum(
        disable_password_expiry(db, dn)
        for dn in NON_EXPIRING_SERVICE_ACCOUNTS.values()
    )

    print(
        "AD mail identity sync complete: "
        f"{len(ALIASES)} identities, {membership_changes} group additions, "
        f"{alias_changes} proxy address additions, {expiry_changes} "
        "service-account password-expiry exemptions added."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"AD mail identity sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
