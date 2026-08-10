# Testing guide

Run all available static checks and tests with `make check`. Backend tests use
Pytest; frontend units use Vitest. CI also performs a production frontend build.
Playwright and scenario suites will be added with the workflow they exercise.

Task completion requires its targeted tests plus a boundary review. Tests must
never depend on TimesFM weights or real client data unless explicitly marked as
an isolated adapter integration test.

