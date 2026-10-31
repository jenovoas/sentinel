"""Real SQL transitions against an explicitly configured disposable PostgreSQL.

Set SENTINEL_GAMMA_TEST_DATABASE_URL to a local sentinel_gamma_test_* database.
Each case owns a random schema and cannot target the production database name.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import json
import os
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.gamma_decision import GammaDecision
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.tenant import Tenant
from app.routers.cortex import EventSubmission
from app.security.gamma_review import review_snapshot
from app.services.cortex_engine import CortexDecisionEngine
from app.services.guardian_gamma import GuardianGammaService
from quantum.yatra_core import S60


class AsyncSessionAdapter:
    """Run the real SQLAlchemy statements synchronously against an isolated DB."""
    def __init__(self, session):
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    def add(self, row):
        self.session.add(row)

    async def commit(self):
        self.session.commit()

    async def refresh(self, row):
        self.session.refresh(row)

    async def rollback(self):
        self.session.rollback()


@pytest.fixture
def review_db():
    configured = os.environ.get("SENTINEL_GAMMA_TEST_DATABASE_URL")
    if not configured:
        pytest.skip("Disposable PostgreSQL URL required for Gamma SQL integration")
    url = make_url(configured)
    if url.host not in ("127.0.0.1", "localhost") or not (url.database or "").startswith("sentinel_gamma_test_"):
        pytest.fail("Gamma integration requires a local disposable sentinel_gamma_test_* database")
    schema = "gamma_review_" + uuid4().hex
    control = create_engine(url)
    with control.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema},public"})
    try:
        for model in (Tenant, Organization, User, GammaDecision, AuditLog):
            model.__table__.create(engine)
        with Session(engine, expire_on_commit=False) as session:
            tenant_id = uuid4()
            session.add_all([
                Tenant(id=tenant_id, name="Gamma integration", slug="gamma-test"),
                Organization(id=tenant_id, name="Gamma integration", slug="gamma-test"),
            ])
            session.commit()
            actor = User(
                id=uuid4(), tenant_id=tenant_id, organization_id=tenant_id,
                email="reviewer@example.test", username="reviewer",
                first_name="Gamma", last_name="Reviewer", role=UserRole.VIEWER,
                is_superuser=True, is_active=True,
            )
            row = GammaDecision(
                guardian_source="beta", decision_type="escalated", context={"event_id": 42},
                evidence={"password": "not-for-review", "source": "guardian_beta"},
                confidence=8424000, status="pending",
                timeout_at=datetime.utcnow() + timedelta(minutes=30),
            )
            session.add_all([actor, row])
            session.commit()
            yield session, AsyncSessionAdapter(session), actor, row
    finally:
        engine.dispose()
        with control.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        control.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("operation,outcome", [("approve", "approved"), ("deny", "denied")])
async def test_review_persists_exact_actor_snapshot_and_single_transition(review_db, operation, outcome):
    session, db, actor, row = review_db
    service = GuardianGammaService(db)
    assert await getattr(service, f"{operation}_decision")(row.id, "Reviewed evidence", actor=actor)
    session.expire_all()
    stored = session.get(GammaDecision, row.id)
    assert stored.status == stored.human_decision == outcome
    assert stored.human_feedback == "Reviewed evidence"
    assert stored.decided_at is not None
    assert stored.evidence["password"] == "not-for-review"  # Original is preserved.
    audits = session.execute(select(AuditLog.__table__)).mappings().all()
    assert len(audits) == 1
    audit = audits[0]
    assert audit["user_id"] == actor.id
    assert audit["tenant_id"] == actor.tenant_id
    assert audit["organization_id"] == actor.organization_id
    assert audit["action"] == f"gamma.{outcome}"
    assert audit["resource"] == f"gamma_decision:{row.id}"
    details = json.loads(audit["details"])
    assert details["actor_id"] == str(actor.id)
    assert details["decision_id"] == row.id
    assert details["context"] == {"event_id": 42}
    assert details["evidence"]["password"] == "[REDACTED]"
    assert details["confidence_s60_raw"] == 8424000
    other = "deny" if operation == "approve" else "approve"
    assert not await getattr(service, f"{other}_decision")(row.id, "Overwrite", actor=actor)
    assert not await getattr(service, f"{operation}_decision")(row.id, "Retry", actor=actor)
    session.expire_all()
    assert session.get(GammaDecision, row.id).human_feedback == "Reviewed evidence"
    assert len(session.execute(select(AuditLog.__table__)).all()) == 1


@pytest.mark.asyncio
async def test_audit_failure_rolls_back_review(review_db, monkeypatch):
    session, db, actor, row = review_db
    async def fail_commit():
        raise RuntimeError("audit storage unavailable")
    monkeypatch.setattr(db, "commit", fail_commit)
    with pytest.raises(RuntimeError, match="audit storage"):
        await GuardianGammaService(db).approve_decision(row.id, "Reviewed", actor=actor)
    session.expire_all()
    assert session.get(GammaDecision, row.id).status == "pending"
    assert session.execute(select(AuditLog.__table__)).all() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["expired", "not-superuser", "inactive"])
async def test_invalid_review_does_not_mutate_or_audit(review_db, state):
    session, db, actor, row = review_db
    if state == "expired":
        row.timeout_at = datetime.utcnow() - timedelta(seconds=1)
        session.commit()
        assert not await GuardianGammaService(db).deny_decision(row.id, "Late", actor=actor)
    else:
        if state == "inactive":
            actor.is_active = False
        else:
            actor.is_superuser = False
        with pytest.raises(PermissionError):
            await GuardianGammaService(db).deny_decision(row.id, "Rejected", actor=actor)
    session.expire_all()
    assert session.get(GammaDecision, row.id).status == "pending"
    assert session.execute(select(AuditLog.__table__)).all() == []


@pytest.mark.asyncio
async def test_pending_projection_is_sanitized_without_mutating_original(review_db):
    session, db, _, row = review_db
    pending = await GuardianGammaService(db).get_pending_decisions()
    assert pending[0]["guardian"] == "beta"
    assert pending[0]["evidence"]["password"] == "[REDACTED]"
    assert session.get(GammaDecision, row.id).evidence["password"] == "not-for-review"


@pytest.mark.asyncio
@pytest.mark.parametrize("source,guardian", [
    ("guardian_alpha", "alpha"), ("guardian_beta", "beta"),
    ("guardian_cognitive", "cognitive"), ("ai_guardian", "ai"),
    ("float_detector", "float"), ("guardian_gamma", "gamma"),
])
async def test_cortex_escalation_preserves_real_source_and_s60(review_db, source, guardian):
    session, db, _, _ = review_db
    assert EventSubmission(event_type="process", source=source, data={}).source == source
    decision = SimpleNamespace(
        id=99, event_id=42, decision_type="escalate", patterns_detected=["ambiguous"],
        reasoning="Human review", escalated_to_gamma=None,
    )
    engine = object.__new__(CortexDecisionEngine)
    engine.db = db
    confidence = S60(0, 39, 0)
    await engine._escalate_to_gamma(decision, {"source": source, "event_type": "process"}, confidence)
    assert decision.escalated_to_gamma is not None
    stored = session.get(GammaDecision, decision.escalated_to_gamma)
    assert stored.guardian_source == guardian
    assert stored.context["source"] == source
    assert stored.context["cortex_decision_id"] == 99
    assert stored.context["event_id"] == 42
    assert stored.evidence["source"] == source
    assert stored.confidence == confidence.to_base_units()


@pytest.mark.asyncio
async def test_unknown_source_is_rejected_in_schema_and_engine(review_db):
    session, db, _, _ = review_db
    with pytest.raises(ValidationError):
        EventSubmission(event_type="process", source="simulation", data={})
    engine = object.__new__(CortexDecisionEngine)
    engine.db = db
    with pytest.raises(ValueError, match="validated guardian source"):
        await engine._escalate_to_gamma(SimpleNamespace(), {"source": "simulation"}, S60(0, 39, 0))
    assert len(session.execute(select(GammaDecision)).all()) == 1


def test_review_snapshot_redacts_nested_secrets_and_bounds_untrusted_text():
    value = {"authorization": "Bearer private", "nested": {"api_key": "hidden", "text": "token=hidden\x00"}, "large": "x" * 20000}
    clean = review_snapshot(value)
    serialized = json.dumps(clean)
    assert "hidden" not in serialized and "private" not in serialized
    assert "TRUNCATED" in serialized
    assert "\x00" not in clean["nested"]["text"]
    assert value["nested"]["api_key"] == "hidden"


@pytest.mark.parametrize("text", [
    'password="two word secret"',
    "passphrase='two word secret'",
    "postgresql://user:secret@database/app",
    "Bearer secret",
    "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----",
])
def test_review_snapshot_redacts_credentials_in_free_text(text):
    assert "secret" not in review_snapshot({"text": text})["text"]


def test_concurrent_review_has_one_winner_and_one_audit(review_db):
    session, _, actor, row = review_db
    engine = session.get_bind()
    decision_id = row.id
    identity = SimpleNamespace(
        id=actor.id, tenant_id=actor.tenant_id, organization_id=actor.organization_id,
        is_active=True, is_superuser=True,
    )
    barrier = Barrier(2)

    def resolve(operation):
        with Session(engine, expire_on_commit=False) as isolated_session:
            service = GuardianGammaService(AsyncSessionAdapter(isolated_session))
            barrier.wait(timeout=10)
            return asyncio.run(
                getattr(service, f"{operation}_decision")(decision_id, operation, actor=identity)
            )

    with ThreadPoolExecutor(max_workers=2) as workers:
        approve = workers.submit(resolve, "approve")
        deny = workers.submit(resolve, "deny")
        outcomes = {"approve": approve.result(timeout=20), "deny": deny.result(timeout=20)}
    assert sorted(outcomes.values()) == [False, True]
    winner = next(operation for operation, succeeded in outcomes.items() if succeeded)
    session.expire_all()
    stored = session.get(GammaDecision, decision_id)
    assert stored.human_feedback == winner
    assert stored.status == ("approved" if winner == "approve" else "denied")
    audits = session.execute(select(AuditLog.__table__)).mappings().all()
    assert len(audits) == 1
    assert audits[0]["user_id"] == identity.id
    assert audits[0]["action"] == f"gamma.{stored.status}"
