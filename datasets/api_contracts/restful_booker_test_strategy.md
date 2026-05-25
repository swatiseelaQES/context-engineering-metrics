# Restful Booker Test Strategy

This demo generates API tests from the OpenAPI-style contract and runs them against `https://restful-booker.herokuapp.com`.

## Scope

Generated tests should cover:

1. Health check through `GET /ping`.
2. Booking ID listing through `GET /booking`.
3. Create/read/delete flow through `POST /booking`, `GET /booking/{id}`, and `DELETE /booking/{id}`.
4. Auth token creation through `POST /auth`.
5. Partial update through `PATCH /booking/{id}` when an auth token is available.
6. Negative checks for invalid IDs or missing auth where useful.

## Stability rules

Restful Booker is a public practice API, so generated tests should avoid assuming any specific preloaded booking IDs. Tests should create their own booking when they need stable data.

## SSL verification

For this demo, SSL verification is controlled by environment variables and defaults to `false`:

- `RESTFUL_BOOKER_VERIFY_SSL=false`
- `OPENAI_VERIFY_SSL=false`

This is intentionally configurable because some corporate machines intercept SSL traffic. Do not use disabled SSL verification as a production default.
