"""Write tools must refuse unknown or wrong-type IDs instead of reporting success.

Things silently ignores (and pops a modal error dialog for) URL-scheme updates
that target an ID it can't find, while the tool used to report success. These
tests pin the pre-flight lookup that prevents both.
"""
import pytest
from things_mcp.server import update_todo, update_project, bulk_update_todos


def _db(items):
    return lambda uuid, default=None, **kw: items.get(uuid, default)


@pytest.mark.asyncio
async def test_update_todo_unknown_id_does_not_execute(mocker):
    mocker.patch('things.get', side_effect=_db({}))
    mock_exec = mocker.patch('things_mcp.server.url_scheme.execute_url')
    result = await update_todo(id="BOGUS", title="x")
    mock_exec.assert_not_called()
    assert "No to-do found" in result and "BOGUS" in result


@pytest.mark.asyncio
async def test_update_todo_rejects_project_id(mocker):
    mocker.patch('things.get', side_effect=_db({"p1": {"uuid": "p1", "type": "project"}}))
    mock_exec = mocker.patch('things_mcp.server.url_scheme.execute_url')
    result = await update_todo(id="p1", title="x")
    mock_exec.assert_not_called()
    assert "is a project" in result and "update_project" in result


@pytest.mark.asyncio
async def test_update_todo_known_id_executes(mocker):
    mocker.patch('things.get', side_effect=_db({"t1": {"uuid": "t1", "type": "to-do"}}))
    mocker.patch('things.token', return_value='tok')
    mock_exec = mocker.patch('things_mcp.server.url_scheme.execute_url')
    result = await update_todo(id="t1", title="x")
    mock_exec.assert_called_once()
    assert "Updated todo" in result


@pytest.mark.asyncio
async def test_update_project_unknown_id_does_not_execute(mocker):
    mocker.patch('things.get', side_effect=_db({}))
    mock_exec = mocker.patch('things_mcp.server.url_scheme.execute_url')
    result = await update_project(id="BOGUS", notes="x")
    mock_exec.assert_not_called()
    assert "No project found" in result


@pytest.mark.asyncio
async def test_update_project_rejects_todo_id(mocker):
    mocker.patch('things.get', side_effect=_db({"t1": {"uuid": "t1", "type": "to-do"}}))
    mock_exec = mocker.patch('things_mcp.server.url_scheme.execute_url')
    result = await update_project(id="t1", notes="x")
    mock_exec.assert_not_called()
    assert "is a to-do" in result and "update_todo" in result


@pytest.mark.asyncio
async def test_update_project_known_id_executes(mocker):
    mocker.patch('things.get', side_effect=_db({"p1": {"uuid": "p1", "type": "project"}}))
    mocker.patch('things.token', return_value='tok')
    mock_exec = mocker.patch('things_mcp.server.url_scheme.execute_url')
    result = await update_project(id="p1", notes="x")
    mock_exec.assert_called_once()
    assert "Updated project" in result


@pytest.mark.asyncio
async def test_bulk_update_any_unknown_id_aborts_whole_batch(mocker):
    mocker.patch('things.get', side_effect=_db({"t1": {"uuid": "t1", "type": "to-do"}}))
    mocker.patch('things.token', return_value='tok')
    mock_exec = mocker.patch('things_mcp.server.url_scheme.execute_url')
    result = await bulk_update_todos(ids=["t1", "BOGUS"], completed=True)
    mock_exec.assert_not_called()
    assert "No to-do found" in result and "BOGUS" in result
    assert "nothing was changed" in result.lower()
