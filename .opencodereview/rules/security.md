# Security Review Guidelines (Python / FastAPI)

Security is the highest priority. Be strict.

## Input Validation & Injection
- **All** user input must be validated at the API boundary using Pydantic models.
- Never build SQL queries using f-strings, `%` formatting, or string concatenation. Always use parameterized queries or SQLAlchemy ORM properly.
- Avoid `eval()`, `exec()`, and `pickle.loads()` on any untrusted input.
- Validate and sanitize file paths to prevent path traversal attacks.
- Be extremely careful with `shell=True` in `subprocess` calls — avoid it when user input is involved.

## Secrets & Sensitive Data
- Never hardcode secrets, passwords, API keys, or connection strings.
- Secrets must come from environment variables or a proper secrets manager.
- Logs must **never** contain passwords, tokens, API keys, or PII.
- Use proper redaction when logging sensitive information.

## Authentication & Authorization
- Verify that sensitive endpoints have proper authentication and authorization checks.
- Do not rely on client-side validation for security decisions.
- Check for missing or bypassed auth checks on new endpoints.

## General Secure Coding
- Validate all external inputs at system boundaries.
- Be cautious with deserialization of untrusted data.
- Follow OWASP guidelines for web applications.
- When in doubt, fail securely and log appropriately.