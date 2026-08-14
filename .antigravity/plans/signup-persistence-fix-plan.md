# Implementation Plan: Persist Users Immediately on Signup

## Background & Analysis

Currently, the `/api/v1/auth/signup` endpoint does not store the user in the database. Instead, it generates a temporary JWT `signup_token` containing the registration data (username, email, hashed password). The user is only written to the database when they successfully complete and submit the profile creation form at `/api/v1/users/?signup_token=...`.

### The Problem
1. **No DB Persistence on Signup**: If a user completes the signup page but drops off (closes the tab, encounters an error) before finishing the profile creation page, their account is never stored in the database.
2. **Login Fails**: Because the user is not in the database, trying to log in later results in an `Invalid credentials` (User Not Found) error. They cannot access the dashboard or attempt profile creation again.
3. **Incomplete Client Implementations**: Frontends (like the `frontend-v2` Next.js template) may lack a profile creation screen, meaning signed-up users are never persisted in the database at all.

### Why was it designed this way?
The database schema for `User` (`src/schemas/user.py`) defines `name` and `skills` as required (`nullable=False`):
```python
    name = Column(String, nullable=False)
    skills = Column(ARRAY(String), nullable=False)
```
Since `/signup` only accepts `username`, `email`, and `password`, the user could not be inserted directly into the database without violating these constraints.

---

## Proposed Changes

### 1. Persist User immediately during Signup

#### [MODIFY] `src/controllers/auth/user_signup.py`
Update the `signup` controller to create and save the `UserSchema` record immediately. 
- Use the `payload.username` as the default `name`.
- Use an empty list `[]` as the default `skills`.
- Commit the user to the database.

```python
    # After generating hashed password:
    user = UserSchema(
        user_id=str(uuid4()),
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
        name=payload.username,  # Satisfies nullable=False
        skills=[],             # Satisfies nullable=False
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
```

---

### 2. Update Profile Creation to support existing Users

#### [MODIFY] `src/controllers/user_profile/create_user_profile.py`
Since the user may already exist in the database after the signup step, updating/saving the profile using `createUserProfile` (which executes on the `/profile/new` form submission) will raise a unique constraint error if it blindly attempts to insert a new row with the same `username` and `email`.

Update `create_user_profile` to check if a user with the token's email already exists:
- **If exists**: Update their basic profile fields (`name`, `mobile`, `github_url`, `linkedin_url`, `skills`) instead of inserting a new `UserSchema` row.
- **If not exists** (fallback for backward compatibility): Insert a new `User` row as before.
- Proceed to insert/associate experiences, educations, projects, and leadership records.

```python
    stmt = select(UserSchema).where(UserSchema.email == cred.get("email"))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = UserSchema(
            user_id=str(uuid4()),
            name=user_profile.name,
            username=cred.get("sub"),
            email=cred.get("email"),
            hashed_password=cred.get("hashed_password"),
            is_active=user_profile.is_active,
            mobile=user_profile.mobile,
            github_url=user_profile.github_url,
            linkedin_url=user_profile.linkedin_url,
            skills=user_profile.skills,
        )
        db.add(user)
    else:
        user.name = user_profile.name
        user.mobile = user_profile.mobile
        user.github_url = user_profile.github_url
        user.linkedin_url = user_profile.linkedin_url
        user.skills = user_profile.skills
        user.is_active = user_profile.is_active
```

---

## Verification Plan

### Automated Tests
1. Run the scratch script `test_signup.py` to verify the end-to-end flow programmatically.
2. Verify that a user record is immediately created in the database after the `/signup` API call.
3. Verify that completing the profile updates the existing record instead of throwing constraint violation errors.

### Manual Verification
1. Sign up a new user via API client (e.g. cURL or Postman) to `/api/v1/auth/signup`.
2. Inspect the database directly using psql/client to verify the user is stored.
3. Log in with the newly created credentials to confirm login succeeds.
