# Testing & Validation Framework Specification

This document details the test suites, configurations, testing commands, and verification protocols.

---

## 1. Unit Testing
- **Tooling**: [e.g. Jest / Vitest / PyTest]
- **Location**: Mirroring source directory (`src/some-service.ts` -> `tests/some-service.spec.ts` or inline `src/some-service.test.ts`).
- **Mocks**: Mock external APIs, third-party services, and heavy DB operations.
- **Command**:
  ```bash
  npm run test
  ```

---

## 2. Integration / API Testing
- **Tooling**: [e.g. Supertest / Playwright API]
- **Database**: Runs on a clean, local container database or temporary SQLite instance.
- **Goal**: Verify routing, middleware execution (auth/rate-limiting), DTO payload parsing, and actual database row mutations.
- **Command**:
  ```bash
  npm run test:integration
  ```

---

## 3. End-to-End (E2E) Browser Testing
- **Tooling**: [e.g. Playwright / Cypress / Vercel Agent Browser]
- **Goal**: Full visual verification of key user flows (e.g. landing page -> login -> dashboard -> core workflow).
- **Command**:
  ```bash
  npm run test:e2e
  ```

---

## 4. Pre-Commit Verification Gate
<!-- Specify what commands must execute successfully before a developer or AI commits code. -->

Before checking in code, run:
```bash
# 1. Typecheck
npm run typecheck
# 2. Linting & Formatting checks
npm run lint && npm run format
# 3. Test Suites
npm run test
```
