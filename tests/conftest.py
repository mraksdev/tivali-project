"""Shared fixtures for the Fcle Auth API tests."""

import json
from collections.abc import Iterator
from http import HTTPStatus
from uuid import uuid4

import pytest
import requests
from faker import Faker

BASE_URL = 'https://automation.tivaliclub.com/fcle'
UNIQUE_SUFFIX_LENGTH = 8

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
    suffix = uuid4().hex[:UNIQUE_SUFFIX_LENGTH]
    return f'{fake.unique.user_name()}.{suffix}@example.com'


@pytest.fixture()
def unique_nickname() -> str:
    """Return a unique nickname."""
    suffix = uuid4().hex[:UNIQUE_SUFFIX_LENGTH]
    return f'{fake.unique.user_name()}.{suffix}'


@pytest.fixture()
def signup_payload(unique_email: str) -> dict[str, str]:
    """Return a valid signup request payload."""
    return {
        'email': unique_email,
        'lang': 'en',
    }


@pytest.fixture()
def signed_up_user(
    api_session: requests.Session,
    base_url: str,
    signup_payload: dict[str, str],
) -> dict[str, str]:
    """Register a new user and return the email and signup token."""
    url = f'{base_url}/api/Auth/signup'
    response = api_session.post(url, json=signup_payload)
    assert response.status_code == HTTPStatus.OK
    body = json.loads(response.json())
    return {'email': body['email'], 'token': body['token']}
