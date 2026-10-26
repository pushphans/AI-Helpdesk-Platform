# AI Helpdesk Platform

A backend REST API built with **FastAPI**, **SQLAlchemy (async)**, and **PostgreSQL** for managing support tickets with JWT-based authentication, refresh token rotation, and an **AI triage agent (LangGraph + Google Gemini)** that classifies, summarizes and drafts replies for tickets.

## Features

- **Auth**
  - User registration and login
  - JWT access tokens (PyJWT) with configurable expiry
  - Opaque refresh tokens with **rotation** — every `/auth/refresh-token` call issues a new refresh token and invalidates the old one
  - Password hashing with Argon2 via `pwdlib`
- **Tickets**
  - Create, retrieve, list, update, and **AI-analyze** tickets
  - Per-user ownership — users can only access their own tickets
  - Filter by `status`, `priority`, and title search (`search_term`)
  - Pagination (`page_number`, `page_size`)
- **AI Triage Agent**
  - LangGraph workflow: `ticket_analyzer → find_policy → draft_reply`
  - Structured output (Pydantic schema) for category, suggested priority and summary
  - Category-aware support policy lookup from `ai/utils/policy.json`
  - Customer-facing reply drafting that never invents company policy
  - Model/provider swappable via `.env` (`MODEL_NAME`, `GOOGLE_MODEL_PROVIDER`)
- **Notifications**
  - Per-user notifications, auto-created on ticket creation
  - List with pagination, mark as read/unread
- **Database**
  - Async SQLAlchemy 2.0 (`Mapped` / `mapped_column` style) on `asyncpg`
  - Alembic migrations (autogenerate)
  - Shared enums in `core/enums.py` (single source of truth for tickets + AI)

## Tech Stack

| Layer     | Tech                                        |
|-----------|---------------------------------------------|
| Framework | FastAPI                                     |
| ORM       | SQLAlchemy 2.0 (async)                      |
| Driver    | asyncpg                                     |
| DB        | PostgreSQL                                  |
| Migrations| Alembic                                     |
| Auth      | PyJWT, pwdlib (Argon2)                      |
| AI        | LangGraph, LangChain, langchain-google-genai (Gemini) |
| Settings  | pydantic-settings (`.env` based)            |
| Server    | Uvicorn                                    |
| Packaging | uv                                          |

## Project Structure

```
src/ai_helpdesk_platform/
├── main.py                  # FastAPI app + router registration
├── core/
│   ├── config.py            # Settings (pydantic-settings, reads .env)
│   ├── db.py                # Async engine, Base, session factory, get_db
│   └── enums.py             # Shared TicketStatus / TicketPriority enums
├── auth/
│   ├── router/auth_router.py     # /auth endpoints
│   ├── service/auth_service.py   # register, login, refresh, get_user
│   ├── schema/auth_schema.py     # Pydantic request/response models
│   ├── model/users_model.py      # users table
│   ├── model/refresh_token_model.py  # refresh_tokens table
│   └── uitls/                    # jwt_utils, password_utils
├── tickets/
│   ├── router/ticket_router.py   # /ticket endpoints
│   ├── service/ticket_service.py # create, get, list, update, analyze
│   ├── schema/ticket_schema.py   # Pydantic request/response models
│   └── model/ticket_model.py     # tickets table
├── notifications/
│   ├── router/notification_router.py   # /notifications endpoints
│   ├── service/notification_service.py # list, mark as read
│   ├── schema/notification_schemas.py  # Pydantic models
│   └── model/notification_model.py     # notifications table
└── ai/
    ├── router/triage_router.py          # /ai endpoints
    ├── service/triage_service.py        # runs the workflow with a request schema
    ├── schema/triage_schemas.py         # AI request/response models
    ├── ticket_triage_agent/
    │   ├── workflow.py                  # LangGraph graph (3 nodes) + LLM setup
    │   ├── state.py                     # AgentState (TypedDict)
    │   └── enums.py                     # re-exports core enums
    └── utils/policy.json                # category → support policy
alembic/                    # Migrations (versions/)
```

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL

### Installation

```bash
git clone <repo-url>
cd AI-Helpdesk-Platform
uv sync
```

### Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:<your-password>@localhost:5432/ai_helpdesk

# Auth
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_IN_MINUTES=30
REFRESH_TOKEN_EXPIRY_IN_DAYS=7
JWT_SECRET_KEY=<your-secret-key>

# AI triage agent
GOOGLE_API_KEY=<your-google-ai-studio-key>
MODEL_NAME=gemini-3.5-flash-lite
GOOGLE_MODEL_PROVIDER=google-genai
```

> **Note:** The async PostgreSQL URL must use the `asyncpg` driver — `postgresql+asyncpg://...`. A plain `postgresql://` or `postgresql+async://` will fail with `NoSuchModuleError`.

> **Note:** `.env` is gitignored — never commit real keys. `GOOGLE_MODEL_PROVIDER` accepts both `google-genai` and `google_genai`.

### Database Setup

Create the database, then run migrations:

```bash
uv run alembic upgrade head
```

To autogenerate a migration after changing models:

```bash
uv run alembic revision --autogenerate -m "description"
```

### Run the Server

```bash
uv run uvicorn ai_helpdesk_platform.main:app --reload
```

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Reference

### Auth (`/auth`)

| Method | Endpoint              | Auth Required | Description                              |
|--------|-----------------------|---------------|------------------------------------------|
| POST   | `/auth/register`      | No            | Register a new user                      |
| POST   | `/auth/login`         | No            | Login, returns access + refresh token    |
| POST   | `/auth/refresh-token` | No            | Exchange refresh token for a new pair (rotation) |

**POST `/auth/register`**

```json
{
  "name": "Pushp Hans",
  "email": "pushp@example.com",
  "password": "secret123"
}
```

**POST `/auth/login`**

```json
{
  "email": "pushp@example.com",
  "password": "secret123"
}
```

Response:

```json
{
  "user_id": "uuid",
  "name": "Pushp Hans",
  "email": "pushp@example.com",
  "access_token": "<jwt>",
  "refresh_token": "<opaque-token>",
  "access_token_expiry": 1800,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

**POST `/auth/refresh-token`**

```json
{
  "refresh_token": "<opaque-token-from-login>"
}
```

Response contains a **new** access token and a **new** refresh token. The old refresh token is no longer valid.

### Tickets (`/ticket`)

All ticket endpoints require an `Authorization: Bearer <access_token>` header.

| Method | Endpoint                     | Description                                   |
|--------|------------------------------|-----------------------------------------------|
| POST   | `/ticket/create-ticket`      | Create a ticket for the authenticated user    |
| GET    | `/ticket/get-ticket/{ticket_id}` | Get a single ticket (own tickets only)    |
| GET    | `/ticket/list-tickets`       | List own tickets with filters and pagination  |
| PUT    | `/ticket/update-ticket/{ticket_id}` | Update title/description/status/priority |
| POST   | `/ticket/analyze/{ticket_id}` | Run the AI triage agent on a stored ticket and get category, suggested priority, summary and suggested reply |

**POST `/ticket/create-ticket`**

```json
{
  "title": "Cannot reset password",
  "description": "The reset email never arrives.",
  "status": "OPEN",
  "priority": "HIGH"
}
```

- `title`: 5–50 characters
- `description`: max 200 characters
- `status` (optional): `OPEN` | `IN_PROGRESS` | `RESOLVED` — default `OPEN`
- `priority` (optional): `LOW` | `MEDIUM` | `HIGH` — default `MEDIUM`

**GET `/ticket/list-tickets`** query parameters:

| Param       | Type   | Default | Constraints      |
|-------------|--------|---------|------------------|
| page_size   | int    | 10      | 10–100           |
| page_number | int    | 1       | ≥ 1              |
| search_term | string | —       | matches title (case-insensitive) |
| status      | enum   | —       | filter by status |
| priority    | enum   | —       | filter by priority |

**PUT `/ticket/update-ticket/{ticket_id}`**

```json
{
  "title": "Cannot reset password",
  "description": "The reset email never arrives.",
  "status": "IN_PROGRESS",
  "priority": "HIGH"
}
```

### AI Triage (`/ai`)

`POST /ai/tickets/` runs the LangGraph workflow directly on the payload you send. No auth required (add auth before exposing it publicly).

**Request**

```json
{
  "title": "Cannot download my invoice",
  "description": "The download button on the billing page gives a 500 error.",
  "status": "OPEN",
  "priority": "MEDIUM"
}
```

**Response**

```json
{
  "category": "BILLING",
  "summary": "The customer gets a 500 error when downloading an invoice from the billing page.",
  "suggested_priority": "MEDIUM",
  "suggested_reply": "Hello, thank you for contacting support... Could you please share your transaction reference?"
}
```

**How it works**

```
START ─▶ ticket_analyzer ─▶ find_policy ─▶ draft_reply ─▶ END
          │                   │               │
          │                   └─ reads ai/utils/policy.json
          └─ structured output: category, suggested_priority, summary
                                └─ DraftReplyStructuredOutput: customer-facing reply
```

| Field               | Values                                        |
|---------------------|-----------------------------------------------|
| `category`          | `BUG` \| `BILLING` \| `TECHNICAL` \| `OTHER`  |
| `suggested_priority`| `HIGH` \| `MEDIUM` \| `LOW` (may differ from the ticket's current priority) |
| `summary`           | 1–2 factual sentences, no invented details     |
| `suggested_reply`   | Customer-facing text, policy-bound             |

`POST /ticket/analyze/{ticket_id}` does the same thing but loads the ticket from the database first (requires auth, ticket must belong to the caller).

### Notifications (`/notifications`)

All endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint                                  | Description                          |
|--------|-------------------------------------------|--------------------------------------|
| GET    | `/notifications/get-notifications`        | List own notifications (`page_size`, `page_number`) |
| PUT    | `/notifications/mark-completed/{id}`      | Mark read/unread                     |

**PUT `/notifications/mark-completed/{id}`**

```json
{
  "is_read": true
}
```

## Database Schema

### `users`

| Column       | Type | Notes            |
|--------------|------|------------------|
| id           | UUID | PK, default uuid4|
| name         | text | not null         |
| email        | text | unique, indexed  |
| password_hash| text | not null         |
| created_at   | timestamptz | server default now() |
| updated_at   | timestamptz | auto-updated     |

### `refresh_tokens`

| Column        | Type | Notes             |
|---------------|------|-------------------|
| id            | UUID | PK, default uuid4 |
| user_id       | UUID | FK → users.id     |
| refresh_token | text | rotated on every refresh |
| rt_expiry     | timestamptz | not null    |
| created_at / updated_at | timestamptz | auto  |

### `tickets`

| Column    | Type | Notes                        |
|-----------|------|------------------------------|
| id        | UUID | PK, default uuid4            |
| user_id   | UUID | FK → users.id, indexed       |
| title     | text | not null                     |
| description | text | not null                   |
| status    | enum | OPEN / IN_PROGRESS / RESOLVED, default OPEN |
| priority  | enum | LOW / MEDIUM / HIGH, default MEDIUM |
| created_at / updated_at | timestamptz | auto        |

### `notifications`

| Column    | Type | Notes                              |
|-----------|------|------------------------------------|
| id        | UUID | PK, default uuid4                  |
| user_id   | UUID | FK → users.id, indexed, not null   |
| message   | text | not null                           |
| is_read   | bool | default false                      |
| created_at / updated_at | timestamptz | auto                |

## License

MIT © Pushp Hans
