# API Reference Specifications: [Project Name]

This document details the interface contracts, REST endpoints, payload schemas, and response formats.

---

## 1. Global API Standards

### A. HTTP Headers
- `Content-Type: application/json`
- `Authorization: Bearer <Token>` (required for authenticated requests)

### B. Standard Response Envelopes
<!-- Enforce consistent API responses for success and failure. -->

#### Success Response (HTTP 200/201)
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-06-05T12:00:00.000Z"
}
```

#### Error Response (HTTP 4xx/5xx)
```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Detailed error message describing what went wrong.",
    "details": { ... }
  },
  "timestamp": "2026-06-05T12:00:05.000Z"
}
```

---

## 2. Authentication API (`/auth`)

### `POST /auth/register`
Registers a new user account.
* **Payload**:
  ```json
  {
    "email": "user@example.com",
    "password": "securePassword123"
  }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "data": {
      "user": {
        "id": "user-uuid",
        "email": "user@example.com"
      }
    }
  }
  ```

### `POST /auth/login`
Authenticates user and yields token.
* **Payload**:
  ```json
  {
    "email": "user@example.com",
    "password": "securePassword123"
  }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "data": {
      "accessToken": "jwt-token-string"
    }
  }
  ```

---

## 3. Core Resource API (`/resources`)
<!-- Detail endpoints for your primary domain models. -->

### `GET /resources`
List resources. Supports pagination and filtering via query parameters.
* **Query Parameters**:
  - `page` (number, default: 1)
  - `limit` (number, default: 10)
* **Response**: `ApiResponse<ResourceSummary[]>`

### `POST /resources`
Create a new resource.
* **Payload**:
  ```json
  {
    "name": "Resource Name",
    "description": "Optional description"
  }
  ```
* **Response**: `ApiResponse<ResourceDetail>`
