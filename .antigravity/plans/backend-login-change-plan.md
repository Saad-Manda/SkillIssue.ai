# Feature Plan: backend-login-change-plan

> [!NOTE]
> This plan has been generated through codebase analysis and is optimized for one-pass execution success.

## Feature Overview & Business Value
Currently, the backend login endpoint accepts both `email` and `username` simultaneously and performs an `AND` query on them. This creates a redundant and poor UX requirement where the client must pass both correct credentials to log in. This plan refactors the backend login payload schema to accept a single `username_or_email` field, allowing users to log in with either their email address or username alongside their password. It also aligns the frontend components to submit this simplified payload.

## Architectural Design & Scope
- **Feature Type**: Refactor / Enhancement
- **Complexity**: Low
- **Systems Affected**: FastAPI user auth models, auth routes, login controllers, Next.js frontend API, and Login form submission.
- **Dependencies**: None

---

## Context References

### Mandatory Codebase Files to Read
- [src/models/user_model.py](file:///D:/Work/SkillIssue.ai/src/models/user_model.py) - LoginRequest schema definition
- [src/controllers/auth/user_login.py](file:///D:/Work/SkillIssue.ai/src/controllers/auth/user_login.py) - Main login logic
- [src/controllers/auth/utils.py](file:///D:/Work/SkillIssue.ai/src/controllers/auth/utils.py) - get_user_for_login query helper
- [src/routes/routes_auth.py](file:///D:/Work/SkillIssue.ai/src/routes/routes_auth.py) - Auth API routes
- [frontend-v2/src/lib/api.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/lib/api.ts) - Frontend auth client login request
- [frontend-v2/src/app/(auth)/login/page.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/app/(auth)/login/page.tsx) - Frontend Login form submission

### Files to Create / Modify
- [src/models/user_model.py](file:///D:/Work/SkillIssue.ai/src/models/user_model.py)
- [src/controllers/auth/utils.py](file:///D:/Work/SkillIssue.ai/src/controllers/auth/utils.py)
- [src/controllers/auth/user_login.py](file:///D:/Work/SkillIssue.ai/src/controllers/auth/user_login.py)
- [src/routes/routes_auth.py](file:///D:/Work/SkillIssue.ai/src/routes/routes_auth.py)
- [frontend-v2/src/lib/api.ts](file:///D:/Work/SkillIssue.ai/frontend-v2/src/lib/api.ts)
- [frontend-v2/src/app/(auth)/login/page.tsx](file:///D:/Work/SkillIssue.ai/frontend-v2/src/app/(auth)/login/page.tsx)

---

## Step-by-Step Tasks

### Phase 1: Backend Refactor

#### Task 1.1: UPDATE `src/models/user_model.py`
- **IMPLEMENT**: Refactor `LoginRequest` to use `username_or_email` instead of separate `username` and `email` fields.
- **TARGET CODE**:
```python
class LoginRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
```
- **REPLACEMENT CODE**:
```python
class LoginRequest(BaseModel):
    username_or_email: str
    password: str
```
- **VALIDATION**: Run backend tests to verify code integrity.

#### Task 1.2: UPDATE `src/controllers/auth/utils.py`
- **IMPLEMENT**: Refactor `get_user_for_login` helper query to match either email or username using SQLAlchemy `or_` operator.
- **TARGET CODE**:
```python
async def get_user_for_login(db: AsyncSession, email: str, username: str):
    stmt = (
        select(UserSchema)
        .where(and_(UserSchema.username == username, UserSchema.email == email))
    )
    result = await db.execute(statement=stmt)
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        return None
    return user_obj
```
- **REPLACEMENT CODE**:
```python
async def get_user_for_login(db: AsyncSession, username_or_email: str):
    stmt = (
        select(UserSchema)
        .where(or_(UserSchema.username == username_or_email, UserSchema.email == username_or_email))
    )
    result = await db.execute(statement=stmt)
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        return None
    return user_obj
```
- **VALIDATION**: Run syntax checks on file.

#### Task 1.3: UPDATE `src/controllers/auth/user_login.py`
- **IMPLEMENT**: Adapt main `login` controller to call the refactored `get_user_for_login` with `payload.username_or_email`.
- **TARGET CODE**:
```python
async def login(db: AsyncSession, payload: LoginRequest):
    logger.info(
        "login controller called for email=%s username=%s",
        payload.email,
        payload.username,
    )
    user = await get_user_for_login(db, payload.email, payload.username)
    if not user:
        logger.warning(
            "login controller invalid credentials: user not found for email=%s username=%s",
            payload.email,
            payload.username,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        logger.warning(
            "login controller invalid credentials: password mismatch for email=%s username=%s",
            payload.email,
            payload.username,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
```
- **REPLACEMENT CODE**:
```python
async def login(db: AsyncSession, payload: LoginRequest):
    logger.info(
        "login controller called for identifier=%s",
        payload.username_or_email,
    )
    user = await get_user_for_login(db, payload.username_or_email)
    if not user:
        logger.warning(
            "login controller invalid credentials: user not found for identifier=%s",
            payload.username_or_email,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        logger.warning(
            "login controller invalid credentials: password mismatch for identifier=%s",
            payload.username_or_email,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
```
- **VALIDATION**: Verify syntax.

#### Task 1.4: UPDATE `src/routes/routes_auth.py`
- **IMPLEMENT**: Adapt `login_endpoint` to correctly log `payload.username_or_email`. Also, implement specific `except HTTPException` handling so 401 status codes are not swallowed and converted to 500 errors.
- **TARGET CODE**:
```python
@router.post("/login", response_model=LoginResponse)
async def login_endpoint(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.info(
        "login_endpoint called for email=%s username=%s",
        payload.email,
        payload.username,
    )
    try:
        response = await login(db, payload)
        logger.info(
            "login_endpoint succeeded for email=%s username=%s",
            payload.email,
            payload.username,
        )
        return response
    except Exception as e:
        logger.exception(
            "login_endpoint failed for email=%s username=%s",
            payload.email,
            payload.username,
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
```
- **REPLACEMENT CODE**:
```python
@router.post("/login", response_model=LoginResponse)
async def login_endpoint(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.info(
        "login_endpoint called for identifier=%s",
        payload.username_or_email,
    )
    try:
        response = await login(db, payload)
        logger.info(
            "login_endpoint succeeded for identifier=%s",
            payload.username_or_email,
        )
        return response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(
            "login_endpoint failed for identifier=%s",
            payload.username_or_email,
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
```
- **VALIDATION**: Run backend tests `pytest src/tests/ -v`.

---

### Phase 2: Frontend Alignments

#### Task 2.1: UPDATE `frontend-v2/src/lib/api.ts`
- **IMPLEMENT**: Update the `authApi.login` parameter definition to submit `username_or_email` instead of separate `username` and `email` properties.
- **TARGET CODE**:
```typescript
  login: (data: { username: string; email: string; password: string }) =>
    request<{ access_token: string; user_id: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
```
- **REPLACEMENT CODE**:
```typescript
  login: (data: { username_or_email: string; password: string }) =>
    request<{ access_token: string; user_id: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
```
- **VALIDATION**: Type check using `npx tsc --noEmit`.

#### Task 2.2: UPDATE `frontend-v2/src/app/(auth)/login/page.tsx`
- **IMPLEMENT**: Update the `onSubmit` handler inside `LoginPage` to send the single `username_or_email` field to the api request.
- **TARGET CODE**:
```typescript
  const onSubmit = async (data: LoginForm) => {
    setApiError(null);
    try {
      const res = await authApi.login({
        username: data.email,
        email: data.email,
        password: data.password,
      });
```
- **REPLACEMENT CODE**:
```typescript
  const onSubmit = async (data: LoginForm) => {
    setApiError(null);
    try {
      const res = await authApi.login({
        username_or_email: data.email,
        password: data.password,
      });
```
- **VALIDATION**: Run compilation check `npx tsc --noEmit` from `frontend-v2/`.

---

## Test & Manual Validation Checklist

### Automated Validation Commands
From the project root:
```bash
# Backend unit tests
pytest src/tests/ -v
```
From the `frontend-v2` directory:
```bash
# Frontend compile check
npx tsc --noEmit
```

### Manual Validation Steps
1. Start the FastAPI backend and Next.js frontend dev servers.
2. Attempt logging in from the UI using a registered email address and correct password.
3. Attempt logging in from the UI using a registered username and correct password.
4. Verify that entering an incorrect email or password shows the proper error alerts instead of throwing 500 status responses.
