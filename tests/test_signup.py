"""Tests for the Auth signup endpoint."""

import json
import re
from http import HTTPStatus

import requests

TOKEN_PATTERN = re.compile(r'^[a-f0-9]{32}$')


def decode_signup_response(response: requests.Response) -> dict[str, str]:
    """Decode the double-encoded JSON body of a signup response."""
    return json.loads(response.json())


class TestAuthSignup:
    """Tests for the POST /api/Auth/signup endpoint."""

    def test_signup_success(
        self,
        api_session: requests.Session,
        base_url: str,
        signup_payload: dict[str, str],
    ) -> None:
        """Register a user and verify the returned data and token."""
        # Arrange.
        url = f'{base_url}/api/Auth/signup'

        # Act.
        response = api_session.post(url, json=signup_payload)

        # Assert.
        assert response.status_code == HTTPStatus.OK
        assert response.headers['Content-Type'].startswith(
            'application/json'
        )
        body = decode_signup_response(response)
        assert body['email'] == signup_payload['email']
        assert body['lang'] == signup_payload['lang']
        assert TOKEN_PATTERN.fullmatch(body['token'])

    def test_signup_default_language(
        self,
        api_session: requests.Session,
        base_url: str,
        unique_email: str,
    ) -> None:
        """Register without lang and verify the default language."""
        # Arrange.
        url = f'{base_url}/api/Auth/signup'
        payload = {'email': unique_email}

        # Act.
        response = api_session.post(url, json=payload)

        # Assert.
        assert response.status_code == HTTPStatus.OK
        body = decode_signup_response(response)
        assert body['email'] == unique_email
        assert body['lang'] == 'en'
