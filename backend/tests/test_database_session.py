from unittest.mock import MagicMock, patch

import pytest

from app.database import session as db_module


@patch("app.database.session.SessionLocal")
def test_get_db_yields_session_and_closes_it(mock_session_local):
    session = MagicMock()
    mock_session_local.return_value = session

    generator = db_module.get_db()
    assert next(generator) is session
    session.close.assert_not_called()

    with pytest.raises(StopIteration):
        next(generator)
    session.close.assert_called_once()


@patch("app.database.session.SessionLocal")
def test_get_db_closes_session_when_request_fails(mock_session_local):
    session = MagicMock()
    mock_session_local.return_value = session

    generator = db_module.get_db()
    next(generator)

    with pytest.raises(RuntimeError):
        generator.throw(RuntimeError("request failed"))
    session.close.assert_called_once()
