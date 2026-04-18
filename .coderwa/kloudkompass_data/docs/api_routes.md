# StatWoX API Route Map

A catalog of available REST endpoints and their primary functions.

## Authentication (`/api/auth`)
- `POST /register`: New user creation (Bcrypt).
- `POST /login`: JWT issuance (Refresh Token rotation).
- `POST /logout`: Session revocation.
- `GET /me`: Current user session details.
- `POST /refresh`: JWT rotation endpoint.
- `/forgot-password`: Email reset request.
- `/reset-password`: Token-based password update.
- `/verify-email/*`: OTP validation/request.
- `/2fa/*`: TOTP setup and verification.
- `/google`, `/linkedin`, `/digilocker`: OAuth provider routes.

## Surveys (`/api/surveys`)
- `GET /`: Feed of public/private surveys.
- `POST /`: Create survey (monolithic nested creator).
- `[id]/respond`: Submit response payload.
- `[id]/publish`: Transition to active state.
- `[id]/close`: Transition to end state.
- `[id]/analytics`: High-level data synthesis.
- `[id]/export/csv`: Raw data stream.

## User & Social
- `GET /users/me`: Extended user profile.
- `POST /users/[id]/follow`: Follower logic.
- `GET /feed`: Trending algorithms.
- `POST /comments/[id]`: Recursive threading.
- `POST /notifications`: System/social updates.

## AI & Data
- `POST /ai/generate-questions`: GLM-5 prompt wrapper.
- `GET /question-bank`: Reusable question discovery.
- `POST /upload`: Cloudflare R2 presigned URL / direct upload.

## Infrastructure
- `GET /health`: DB and service connectivity check.
- `GET /audit`: System-level action tracking.
- `GET /cron/sync-counts`: Denormalized count aggregation.
- `GET /docs`: OpenAPI/Swagger documentation.