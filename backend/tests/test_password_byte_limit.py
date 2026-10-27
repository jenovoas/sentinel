from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import UserCreate as LegacyUserCreate
from app.schemas.users import UserCreate, UserUpdate
from app.security.auth import get_password_hash, verify_password


def test_bcrypt_hashing_rejects_over_72_utf8_bytes_and_keeps_legacy_hashes():
    password = "ñ" * 36  # 72 UTF-8 bytes
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    with pytest.raises(ValueError, match="72 UTF-8 bytes"):
        get_password_hash(password + "x")
    assert verify_password(password + "x", hashed) is False


def test_user_schemas_reject_passwords_over_bcrypt_byte_limit():
    too_long = "ñ" * 37  # 74 UTF-8 bytes, although only 37 characters
    with pytest.raises(ValidationError):
        LegacyUserCreate(email="one@example.com", username="one", password=too_long)
    with pytest.raises(ValidationError):
        UserCreate(
            email="two@example.com",
            username="two",
            first_name="Two",
            last_name="User",
            password=too_long,
            organization_id=uuid4(),
        )
    with pytest.raises(ValidationError):
        UserUpdate(password=too_long)
