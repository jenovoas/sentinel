from uuid import uuid4

import pytest
from sqlalchemy import event

from app.models.user import User, sync_tenant_id


def test_user_role_enum_uses_persisted_database_labels():
    assert User.__table__.c.role.type.enums == ["admin", "member", "viewer"]


def test_user_timestamps_have_database_defaults():
    assert User.__table__.c.created_at.server_default is not None
    assert User.__table__.c.updated_at.server_default is not None


def test_insert_and_update_hooks_sync_matching_tenant_id():
    organization_id = uuid4()
    user = User(organization_id=organization_id, tenant_id=None)

    sync_tenant_id(None, None, user)

    assert user.tenant_id == organization_id
    assert event.contains(User, "before_insert", sync_tenant_id)
    assert event.contains(User, "before_update", sync_tenant_id)


def test_tenant_sync_rejects_divergent_ids():
    user = User(organization_id=uuid4(), tenant_id=uuid4())

    with pytest.raises(ValueError, match="must match"):
        sync_tenant_id(None, None, user)
