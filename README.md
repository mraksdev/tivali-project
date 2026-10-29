# Tivali Registration API Tests

Automated API tests for the two-step account registration of the Fcle API:
signup, password setup and sign-in.

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

Every test registers a new user with a unique email and nickname, so the
suite can be run repeatedly without data conflicts.

Run a single test class or filter tests by name:

```bash
pytest tests/test_signup.py::TestAuthSignup -v
pytest tests/test_signup.py::TestSetPassword -v
pytest tests/test_signup.py -k password -v
```

## Project structure

```
project/
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # fixtures and test settings
│   └── test_signup.py   # tests for the registration endpoints
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
| `unique_nickname` | function | unique nickname for every test run |
| `signup_payload` | function | valid signup request payload |
| `signed_up_user` | function | registers a user and returns its email and token |

### Test cases

`TestAuthSignup` covers `POST /api/Auth/signup`:

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

`TestSetPassword` covers `POST /api/Auth/set-password` and
`POST /api/Auth/login`:

| Test | Cases | Expected result |
|---|---|---|
| `test_set_password_success` | 1 | 200, JWT with three parts |
| `test_login_with_new_password` | 1 | 200, JWT for the new password |
| `test_login_with_wrong_password` | 1 | 410, `user.loginMethod.invalid` |
| `test_set_password_weak_password` | 4 | 409, `user.password.isShort`, `notStrong` or `forbiddenSymbols` |
| `test_set_password_min_password_length` | 1 | 200, six-character password accepted |
| `test_set_password_nickname_boundaries` | 2 | 200, nicknames of 1 and 50 characters |
| `test_set_password_invalid_nickname` | 3 | 409, `user.nickname.tooLong`, `notNull` or `isRequired` |
| `test_set_password_invalid_token` | 1 | 410, `user.token.invalid` |
| `test_set_password_reused_token` | 1 | 410, `user.token.invalid` |
| `test_set_password_missing_fields` | 3 | 409, `user.token.notNull` or `user.newPassword.notNull` |

Total: 43 test cases.

## Expected output

```bash
$ pytest tests/ -v
============================= test session starts =============================
...
tests/test_signup.py::TestAuthSignup::test_signup_success PASSED
tests/test_signup.py::TestSetPassword::test_set_password_success PASSED
...
============================== 43 passed in 20.12s ==============================
```

## API notes

- Base URL: <https://automation.tivaliclub.com/fcle>
- Swagger: <https://automation.tivaliclub.com/fcle/swagger/index.html>

Registration takes two steps:

1. `POST /api/Auth/signup` accepts `email` (required), `lang` and `utm`
   (optional). There is no password or nickname at this step.
2. `POST /api/Auth/set-password` accepts the `token` from signup,
   `newPassword` and `nickname` (`timezone` is optional) and returns a JWT.

After that `POST /api/Auth/login` accepts `email` and `password` and returns
a JWT as well.

A signup response is a JSON string that has to be decoded twice:

```python
body = json.loads(response.json())
```

The decoded object contains `email`, `lang` and a 32-character hex `token`.

Other behaviour worth knowing:

- a repeated signup for the same email is case-insensitive and returns
  429 `user.signup.resetTokenSent`, not a conflict;
- the signup token is single-use: a second `set-password` request returns
  410 `user.token.invalid`;
- a password must be at least 6 characters long, contain only Latin letters,
  digits and special characters, and meet at least three strength conditions;
- a nickname must be 1 to 50 characters long and does not have to be unique;
- a wrong password on login returns 410 `user.loginMethod.invalid`;
- validation errors have the shape
  `{"error": {"code": ..., "message": ..., "values": ...}}`;
- emails are normalized to lowercase;
- tests create real accounts in the test environment.

## Author

**Alexander Krylov** — [@mraksdev](https://github.com/mraksdev)
