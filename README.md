# Tivali Signup API Tests

Automated API tests for the account signup endpoint of the Fcle API.

## Tech stack

- Python 3.12
- pytest 8.3.3
- requests 2.32.3
- Faker 30.1.0

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with:

```bash
venv\Scripts\activate
```

## Running tests

```bash
pytest tests/ -v
```

Every test generates a unique email with Faker and a UUID suffix, so the
suite can be run repeatedly without data conflicts.

Run a single test class or filter tests by name:

```bash
pytest tests/test_signup.py::TestAuthSignup -v
pytest tests/test_signup.py -k duplicate -v
```

## Project structure

```
project/
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # fixtures and test settings
│   └── test_signup.py   # tests for POST /api/Auth/signup
├── requirements.txt     # pinned dependencies
├── README.md            # project documentation
└── .gitignore           # ignored files
```

### Fixtures

| Fixture | Scope | Purpose |
|---|---|---|
| `base_url` | session | API base URL |
| `api_session` | session | shared `requests.Session` with JSON headers |
| `unique_email` | function | unique email for every test run |
| `signup_payload` | function | valid signup request payload |
| `registered_user` | function | registers a user and returns its email |

### Test cases

| Test | Cases | Expected result |
|---|---|---|
| `test_signup_success` | 1 | 200, email and token in response |
| `test_signup_default_language` | 1 | 200, default language is `en` |
| `test_signup_invalid_email_format` | 11 | 409, `user.email.isInvalid` |
| `test_signup_missing_email` | 3 | 409, `user.email.notNull` or `user.email.isRequired` |
| `test_signup_invalid_language` | 3 | 409, `user.language.isInvalid` |
| `test_signup_malformed_body` | 3 | 409, `validation.failed` |
| `test_signup_unsupported_content_type` | 1 | 415, ProblemDetails response |
| `test_signup_duplicate_email` | 2 | 429, `user.signup.resetTokenSent` |

Total: 25 test cases.

## Expected output

```bash
$ pytest tests/ -v
============================= test session starts =============================
...
tests/test_signup.py::TestAuthSignup::test_signup_success PASSED
tests/test_signup.py::TestAuthSignup::test_signup_default_language PASSED
...
============================== 25 passed in 9.14s ==============================
```

## API notes

- Base URL: <https://automation.tivaliclub.com/fcle>
- Swagger: <https://automation.tivaliclub.com/fcle/swagger/index.html>

`POST /api/Auth/signup` accepts `email` (required), `lang` and `utm`
(optional). The API has no password or username fields.

A successful response is a JSON string that has to be decoded twice:

```python
body = json.loads(response.json())
```

The decoded object contains `email`, `lang` and a 32-character hex `token`.

Other behaviour worth knowing:

- a repeated signup for the same email is case-insensitive and returns
  429 `user.signup.resetTokenSent`, not a conflict;
- validation errors have the shape
  `{"error": {"code": ..., "message": ..., "values": ...}}`;
- emails are normalized to lowercase;
- tests create real accounts in the test environment.

## Author

**Alexander Krylov** — [@mraksdev](https://github.com/mraksdev)
