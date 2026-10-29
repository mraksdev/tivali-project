"""Tests for the Auth signup endpoint."""

import json
import re
from http import HTTPStatus

import pytest
import requests

TOKEN_PATTERN = re.compile(r'^[a-f0-9]{32}$')


def decode_signup_response(response: requests.Response) -> dict[str, str]:
    """Decode the double-encoded JSON body of a signup response."""
    return json.loads(response.json())


def assert_error_response(
    response: requests.Response,
    status_code: int,
    error_code: str,
) -> dict:
    """Assert status and error code of a failed response."""
    assert response.status_code == status_code
    body = response.json()
    assert body['error']['code'] == error_code
    return body


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

    @pytest.mark.parametrize(
        'email',
        [
            'plainaddress',
            'user@',
            '@example.com',
            'user@example',
            'user@.com',
            'user@example.',
            'user@example.c',
            'user @example.com',
            '  spaced@example.com  ',
            'user@@example.com',
            'user@exa_mple.com',
        ],
        ids=[
            'no-at-sign',
            'no-domain',
            'no-local-part',
            'no-dot',
            'no-domain-name',
            'no-tld',
            'short-tld',
            'space-in-local-part',
            'outer-spaces',
            'double-at-sign',
            'underscore-in-domain',
        ],
    )
    def test_signup_invalid_email_format(
        self,
        api_session: requests.Session,
        base_url: str,
        email: str,
    ) -> None:
        """Reject an email that does not match the required format."""
        # Arrange.
        url = f'{base_url}/api/Auth/signup'

        # Act.
        response = api_session.post(url, json={'email': email})

        # Assert.
        body = assert_error_response(
            response,
            HTTPStatus.CONFLICT,
            'user.email.isInvalid',
        )
        assert body['error']['values'] == email

    @pytest.mark.parametrize(
        ('payload', 'error_code'),
        [
            ({}, 'user.email.notNull'),
            ({'email': None}, 'user.email.notNull'),
            ({'email': ''}, 'user.email.isRequired'),
        ],
        ids=['empty-body', 'null-email', 'empty-string'],
    )
    def test_signup_missing_email(
        self,
        api_session: requests.Session,
        base_url: str,
        payload: dict,
        error_code: str,
    ) -> None:
        """Reject a request without a usable email value."""
        # Arrange.
        url = f'{base_url}/api/Auth/signup'

        # Act.
        response = api_session.post(url, json=payload)

        # Assert.
        assert_error_response(
            response,
            HTTPStatus.CONFLICT,
            error_code,
        )

    @pytest.mark.parametrize(
        'lang',
        ['xx', 'english', 'en-US'],
        ids=['unknown-code', 'language-name', 'region-code'],
    )
    def test_signup_invalid_language(
        self,
        api_session: requests.Session,
        base_url: str,
        unique_email: str,
        lang: str,
    ) -> None:
        """Reject a language code that is not supported."""
        # Arrange.
        url = f'{base_url}/api/Auth/signup'
        payload = {'email': unique_email, 'lang': lang}

        # Act.
        response = api_session.post(url, json=payload)

        # Assert.
        body = assert_error_response(
            response,
            HTTPStatus.CONFLICT,
            'user.language.isInvalid',
        )
        assert body['error']['values'] == lang

    @pytest.mark.parametrize(
        'raw_body',
        ['', '[]', '{"email": 123}'],
        ids=['empty-body', 'array', 'non-string-email'],
    )
    def test_signup_malformed_body(
        self,
        api_session: requests.Session,
        base_url: str,
        raw_body: str,
    ) -> None:
        """Reject a body that cannot be parsed as a signup request."""
        # Arrange.
        url = f'{base_url}/api/Auth/signup'

        # Act.
        response = api_session.post(url, data=raw_body)

        # Assert.
        assert_error_response(
            response,
            HTTPStatus.CONFLICT,
            'validation.failed',
        )

    def test_signup_unsupported_content_type(
        self,
        api_session: requests.Session,
        base_url: str,
        signup_payload: dict[str, str],
    ) -> None:
        """Reject a request sent with a non-JSON content type."""
        # Arrange.
        url = f'{base_url}/api/Auth/signup'

        # Act.
        response = api_session.post(
            url,
            data=json.dumps(signup_payload),
            headers={'Content-Type': 'text/plain'},
        )

        # Assert.
        assert response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
        body = response.json()
        assert body['status'] == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
        assert body['title'] == 'Unsupported Media Type'
