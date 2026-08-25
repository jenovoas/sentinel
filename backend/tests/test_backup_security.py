# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.routers import backup


def test_trigger_backup_logic_unauthorized_path():
    # 3 calls to abspath: __file__, backup_script, project_root
    with patch('os.path.abspath', side_effect=["/app/backend/app/routers/backup.py", "/tmp/malicious.sh", "/app"]):
        with patch('os.path.dirname', return_value="/app/backend/app/routers"):
            import asyncio
            try:
                asyncio.run(backup.trigger_backup())
            except HTTPException as e:
                assert e.status_code == 403
                assert "Unauthorized script path" in e.detail
            else:
                pytest.fail("Should have raised HTTPException")

def test_trigger_backup_logic_not_executable():
    # 3 calls to abspath: __file__, backup_script, project_root
    with patch('os.path.abspath', side_effect=["/app/backend/app/routers/backup.py", "/app/scripts/backup/backup.sh", "/app"]):
        with patch('os.path.dirname', return_value="/app/backend/app/routers"):
            with patch('os.path.exists', return_value=True):
                with patch('os.access', return_value=False):
                    import asyncio
                    try:
                        asyncio.run(backup.trigger_backup())
                    except HTTPException as e:
                        assert e.status_code == 403
                        assert "not executable" in e.detail
                    else:
                        pytest.fail("Should have raised HTTPException")

def test_trigger_backup_logic_world_writable():
    # 3 calls to abspath
    with patch('os.path.abspath', side_effect=["/app/backend/app/routers/backup.py", "/app/scripts/backup/backup.sh", "/app"]):
        with patch('os.path.dirname', return_value="/app/backend/app/routers"):
            with patch('os.path.exists', return_value=True):
                with patch('os.access', return_value=True):
                    mock_stat = MagicMock()
                    mock_stat.st_mode = 0o100777
                    with patch('os.stat', return_value=mock_stat):
                        import asyncio
                        try:
                            asyncio.run(backup.trigger_backup())
                        except HTTPException as e:
                            assert e.status_code == 403
                            assert "world-writable" in e.detail
                        else:
                            pytest.fail("Should have raised HTTPException")
