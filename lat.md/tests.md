# Tests

Test specifications for the project. Integration tests exercise real services/routes via the Litestar test client; see the suite layout under `[[tests]]` (unit tests mirror each library module, integration tests cover domain routes/services).

## User login

Login issues a JWT access token for valid credentials and rejects bad ones; covered by `tests/integration/accounts/routes/test_access.py`.

### Issues access token for valid credentials

POST `/api/access/login` with correct email/password returns an access token whose token type is bearer.

### Rejects invalid credentials

Login with a wrong password is rejected with a non-success status (403 in the current client behavior for invalid credentials; `tests/integration/accounts/routes/test_access.py::test_login_invalid_credentials`).