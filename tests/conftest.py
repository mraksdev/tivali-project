"""Shared fixtures for the Fcle Auth API tests."""

from collections.abc import Iterator
from http import HTTPStatus
from uuid import uuid4

import pytest
import requests
from faker import Faker

BASE_URL = 'https://automation.tivaliclub.com/fcle'
EMAIL_SUFFIX_LENGTH = 8

fake = Faker()


@pytest.fixture(scope='session')
def base_url() -> str:
    """Return the API base URL."""
    return BASE_URL


@pytest.fixture(scope='session')
def api_session() -> Iterator[requests.Session]:
    """Return a shared HTTP session closed after the test run."""
    session = requests.Session()
    session.headers.update(
        {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    yield session
    session.close()


@pytest.fixture()
def unique_email() -> str:
    """Return a unique email address."""
    suffix = uuid4().hex[:EMAIL_SUFFIX_LENGTH]
    return f'{fake.unique.user_name()}.{suffix}@example.com'


@pytest.fixture()
def signup_payload(unique_email: str) -> dict[str, str]:
    """Return a valid signup request payload."""
    return {
        'email': unique_email,
        'lang': 'en',
    }


@pytest.fixture()
def registered_user(
    api_session: requests.Session,
    base_url: str,
    signup_payload: dict[str, str],
) -> str:
    """Register a new user and return the email address."""
    url = f'{base_url}/api/Auth/signup'
    response = api_session.post(url, json=signup_payload)
    assert response.status_code == HTTPStatus.OK
    return signup_payload['email']
