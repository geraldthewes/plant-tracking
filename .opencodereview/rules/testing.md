# Testing Review Guidelines (Python / Pytest)

## Test Quality
- Every public function should have meaningful tests covering both happy paths and error conditions.
- Test names must be descriptive and explain the scenario + expected outcome (e.g., `test_raises_value_error_when_email_is_empty`).
- Test error paths explicitly — do not only test the success case.
- Use property-based testing (Hypothesis) for data transformation, parsing, and encoding logic when appropriate.

## Test Structure & Practices
- Follow clear Arrange / Act / Assert structure.
- Use pytest fixtures properly for setup and teardown.
- Avoid over-mocking of business logic. Mock at I/O boundaries (database, external APIs, file system).
- Do not make real network calls or hit real databases in unit tests.
- Clearly mark integration tests (e.g., using `@pytest.mark.integration`).

## FastAPI Testing
- Use `TestClient` or `AsyncClient` appropriately.
- Test dependency overrides correctly when needed.
- Verify both status codes and response bodies/schemas.