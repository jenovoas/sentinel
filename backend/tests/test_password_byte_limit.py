from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import UserCreate as DirectoryUserCreate
from app.schemas.users import UserCreate, UserUpdate
from app.security.auth import get_password_hash, verify_password


def test_bcrypt_hashing_rejects_over_72_utf8_bytes_and_keeps_legacy_hashes():
    password = "ñ" * 36  # 72 UTF-8 bytes
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    with pytest.raises(ValueError, match="72 UTF-8 bytes"):
        get_password_hash(password + "x")
    assert verify_password(password + "x", hashed) is False


def test_user_schemas_reject_local_password_fields():
    with pytest.raises(ValidationError):
        DirectoryUserCreate(
            email="one@example.com",
            username="one",
            first_name="One",
            last_name="User",
            organization_id=uuid4(),
            password="any-password",
        )
    with pytest.raises(ValidationError):
        UserCreate(
            email="two@example.com",
            username="two",
            first_name="Two",
            last_name="User",
            organization_id=uuid4(),
            password="any-password",
        )
    with pytest.raises(ValidationError):
        UserUpdate(password="any-password")
