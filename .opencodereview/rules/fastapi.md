# FastAPI & Pydantic Review Guidelines

Focus on modern FastAPI and Pydantic best practices.

## API Design
- Use Pydantic models for **all** request and response validation.
- Prefer dependency injection using `Depends()` over global state or module-level variables.
- Always define `response_model` on endpoints when a Pydantic model exists.
- Avoid returning raw dictionaries from endpoints when a proper response model is available.
- Use `Annotated` for path/query parameters and dependencies (modern Python style).
- Keep routers thin — move business logic into service layers.
- Use `APIRouter` for organizing routes into logical modules.

## Dependency Injection
- Use FastAPI's dependency injection system (`Depends`) for database sessions, authentication, and services.
- Never instantiate repositories or services directly inside endpoint functions.
- Prefer constructor injection or `Depends` over passing dependencies manually.

## Error Handling
- Use FastAPI's `HTTPException` (or custom exception handlers) for API errors.
- Return proper HTTP status codes that match the situation.
- Provide clear, actionable error messages to clients.
- Log unexpected errors with sufficient context (but never log secrets or PII).

## Background Tasks & Async
- Use `BackgroundTasks` appropriately for fire-and-forget operations.
- Be careful with async database operations and connection handling.
- Ensure proper cleanup of resources in async contexts.