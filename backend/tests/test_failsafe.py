import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from app.services.failsafe_service import FailSafeService
from app.models.failsafe import FailSafeExecution, FailSafeStatus

@pytest.mark.asyncio
async def test_create_execution():
    db = AsyncMock()
    playbook = "backup_recovery"
    triggered_by = "test"
    severity = "high"

    execution = await FailSafeService.create_execution(db, playbook, triggered_by, severity)

    assert execution.playbook == playbook
    assert execution.triggered_by == triggered_by
    assert execution.severity == severity
    assert execution.status == FailSafeStatus.TRIGGERED
    db.add.assert_called_once()
    db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_execution_status():
    db = AsyncMock()
    execution_id = uuid4()
    mock_execution = FailSafeExecution(id=execution_id, playbook="test")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_execution
    db.execute.return_value = mock_result

    updated = await FailSafeService.update_execution_status(
        db, execution_id, FailSafeStatus.SUCCESS, "Success"
    )

    assert updated.status == FailSafeStatus.SUCCESS
    assert updated.outcome == "Success"
    assert updated.finished_at is not None
    db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_get_failsafe_status_empty():
    db = AsyncMock()

    # Mocking multiple queries in FailSafeService.get_failsafe_status
    mock_total = MagicMock()
    mock_total.scalar.return_value = 0

    mock_recent = MagicMock()
    mock_recent.mappings.return_value.first.return_value = {"total": 0, "success": 0}

    mock_last = MagicMock()
    mock_last.scalar.return_value = None

    mock_pb = MagicMock()
    mock_pb.mappings.return_value.first.return_value = {
        "count": 0, "success": 0, "last_run": None
    }

    db.execute.side_effect = [mock_total, mock_recent, mock_last,
                             mock_pb, mock_pb, mock_pb, mock_pb, mock_pb, mock_pb]

    status = await FailSafeService.get_failsafe_status(db)

    assert status["total_executions"] == 0
    assert status["success_rate_30d"] == 0.0
    assert status["last_auto_remediation"] == "Never"
    assert len(status["playbooks"]) == 6
