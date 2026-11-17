
# tests/integration/test_full_coverage.py

from unittest.mock import MagicMock, patch

import pytest

import app.database as database_module
from app.models.user import User


def test_get_db_creates_and_closes_session():
    """Verify database session creation and cleanup."""

    mock_session = MagicMock()

    with patch.object(
        database_module,
        "SessionLocal",
        return_value=mock_session
    ):
        generator = database_module.get_db()

        session = next(generator)

        assert session is mock_session

        with pytest.raises(StopIteration):
            next(generator)

        mock_session.close.assert_called_once()


def test_get_db_closes_session_on_exception():
    """Verify cleanup when an exception occurs."""

    mock_session = MagicMock()

    with patch.object(
        database_module,
        "SessionLocal",
        return_value=mock_session
    ):
        generator = database_module.get_db()

        assert next(generator) is mock_session

        with pytest.raises(
            RuntimeError,
            match="Test database error"
        ):
            generator.throw(
                RuntimeError("Test database error")
            )

        mock_session.close.assert_called_once()


def test_register_invalid_user_data():
    """Verify invalid registration data is rejected."""

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    invalid_user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "invalid-email",
        "username": "testuser",
        "password": "SecurePass123",
    }

    with pytest.raises(ValueError):
        User.register(mock_db, invalid_user_data)


def test_authenticate_nonexistent_user():
    """Verify authentication fails when a user doesn't exist."""

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = User.authenticate(
        mock_db,
        username="nonexistent_user",
        password="SecurePass123",
    )

    assert result is None


def test_authenticate_incorrect_password():
    """Verify authentication rejects an incorrect password."""

    mock_db = MagicMock()

    user = User(
        first_name="Test",
        last_name="User",
        email="coverage@example.com",
        username="coverageuser",
        password_hash=User.hash_password("CorrectPass123"),
    )

    mock_db.query.return_value.filter.return_value.first.return_value = user

    result = User.authenticate(
        mock_db,
        username="coverageuser",
        password="WrongPass123",
    )

    assert result is None
    mock_db.commit.assert_not_called()
