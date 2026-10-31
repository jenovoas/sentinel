"""Authenticate human users against the authoritative Samba AD directory."""

from __future__ import annotations

import ssl
from dataclasses import dataclass
from urllib.parse import urlparse
from uuid import UUID

import anyio
from ldap3 import Connection, NONE, Server, SUBTREE, Tls
from ldap3.core.exceptions import LDAPExceptionError
from ldap3.utils.conv import escape_filter_chars

from app.config import get_settings


class DirectoryUnavailable(RuntimeError):
    """AD configuration, network, TLS, or LDAP service is unavailable."""


@dataclass(frozen=True)
class DirectoryIdentity:
    directory_id: str
    user_principal_name: str
    email: str
    display_name: str
    sam_account_name: str
    member_of: frozenset[str]

    @property
    def is_sentinel_admin(self) -> bool:
        group_dn = get_settings().sentinel_admin_group_dn.strip().casefold()
        return bool(group_dn) and group_dn in {
            group.strip().casefold() for group in self.member_of
        }


def _text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def _authenticate_sync(username: str, password: str) -> DirectoryIdentity | None:
    settings = get_settings()
    parsed = urlparse(settings.ldap_url)
    if (
        parsed.scheme != "ldaps"
        or not parsed.hostname
        or parsed.port not in (None, 636)
        or parsed.path not in ("", "/")
        or not settings.ldap_base_dn.strip()
        or not settings.ldap_tls_ca_file.strip()
        or not settings.ldap_tls_servername.strip()
        or parsed.hostname.casefold() != settings.ldap_tls_servername.strip().casefold()
        or not settings.sentinel_admin_group_dn.strip()
    ):
        raise DirectoryUnavailable("AD LDAPS configuration is incomplete or invalid")

    upn = username.strip()
    if "@" not in upn or not password:
        return None

    tls = Tls(
        validate=ssl.CERT_REQUIRED,
        version=ssl.PROTOCOL_TLS_CLIENT,
        ca_certs_file=settings.ldap_tls_ca_file,
    )
    server = Server(
        host=parsed.hostname,
        port=parsed.port or 636,
        use_ssl=True,
        tls=tls,
        get_info=NONE,
        connect_timeout=5,
    )
    connection = Connection(
        server,
        user=upn,
        password=password,
        receive_timeout=5,
        auto_referrals=False,
        raise_exceptions=False,
    )
    try:
        if not connection.bind():
            result_code = (connection.result or {}).get("result")
            if result_code == 49:
                return None
            raise DirectoryUnavailable("AD rejected the bind or is unavailable")

        escaped_upn = escape_filter_chars(upn)
        found = connection.search(
            search_base=settings.ldap_base_dn,
            search_filter=(
                "(&(objectCategory=person)(objectClass=user)"
                f"(userPrincipalName={escaped_upn}))"
            ),
            search_scope=SUBTREE,
            attributes=[
                "objectGUID",
                "userPrincipalName",
                "mail",
                "displayName",
                "sAMAccountName",
                "memberOf",
            ],
            size_limit=2,
        )
        if not found or len(connection.entries) != 1:
            return None

        entry = connection.entries[0]
        raw_attributes = {
            attribute.casefold(): values
            for attribute, values in entry.entry_raw_attributes.items()
        }
        raw_guids = raw_attributes.get("objectguid", [])
        if not raw_guids or len(raw_guids[0]) != 16:
            return None

        member_values = entry["memberOf"].values if "memberOf" in entry else []
        if isinstance(member_values, str):
            member_values = [member_values]

        return DirectoryIdentity(
            directory_id=str(UUID(bytes_le=raw_guids[0])),
            user_principal_name=_text(entry["userPrincipalName"].value) or upn,
            email=_text(entry["mail"].value) or upn,
            display_name=_text(entry["displayName"].value),
            sam_account_name=_text(entry["sAMAccountName"].value),
            member_of=frozenset(_text(group) for group in member_values),
        )
    except DirectoryUnavailable:
        raise
    except (LDAPExceptionError, OSError, ssl.SSLError, ValueError) as exc:
        raise DirectoryUnavailable("AD LDAPS authentication is unavailable") from exc
    finally:
        if connection.bound:
            connection.unbind()


async def authenticate_directory_user(
    username: str, password: str
) -> DirectoryIdentity | None:
    """Run the blocking LDAP bind/search outside the FastAPI event loop."""
    return await anyio.to_thread.run_sync(_authenticate_sync, username, password)
