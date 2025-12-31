import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_tasks_router_exposes_expected_paths():
    pytest.importorskip("httpx")
    from src.app.interfaces.tasks.router import router

    paths = {route.path for route in router.routes}
    assert "/tasks/01-min-job" in paths
    assert "/tasks/05-min-job" in paths
    assert "/tasks/15-min-job" in paths
    assert "/tasks/runtime" in paths


@pytest.mark.asyncio
async def test_task_sync_balance_requires_auth():
    from fastapi import HTTPException
    from src.app.application.account.sync_balance import task_sync_balance

    with pytest.raises(HTTPException) as excinfo:
        await task_sync_balance()
    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_task_update_price_requires_auth():
    from fastapi import HTTPException
    from src.app.application.market.sync_price import task_update_price

    with pytest.raises(HTTPException) as excinfo:
        await task_update_price()
    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_task_update_cost_requires_auth():
    from fastapi import HTTPException
    from src.app.application.market.sync_cost import task_update_cost

    with pytest.raises(HTTPException) as excinfo:
        await task_update_cost()
    assert excinfo.value.status_code == 401
