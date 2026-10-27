from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.routers.backup import trigger_backup


@pytest.mark.asyncio
async def test_backup_trigger_returns_disabled_without_running_script():
    user = SimpleNamespace(is_superuser=True)
    with patch("subprocess.run") as run:
        with pytest.raises(HTTPException) as error:
            await trigger_backup(current_user=user)
    assert error.value.status_code == 503
    run.assert_not_called()
