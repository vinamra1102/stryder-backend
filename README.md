# Stryder Backend

Production-ready FastAPI backend for **Stryder** — a premium wellness and step tracking app.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115 |
| Server | Uvicorn |
| Auth | Google OAuth 2.0 (Authlib) + custom HS256 JWT |
| Fitness data | Google Fit REST API |
| HTTP client | httpx (async) |
| Validation | Pydantic v2 |
| Environment | python-dotenv |

---

## Project Structure

```
app/
├── main.py               # FastAPI app, middleware, lifespan
├── config.py             # All env vars in one place
├── dependencies.py       # get_current_user JWT dependency
├── oauth_client.py       # Authlib Google OAuth registration
├── routers/
│   ├── auth.py           # /auth/* — login, callback, me, refresh, status, logout
│   ├── fitness.py        # /fitness/* — steps, summary, history
│   ├── health.py         # /health
│   └── user.py           # /user/* — settings
├── services/
│   ├── google_fit.py     # Google Fit API calls (async httpx)
│   └── token_service.py  # JWT create / decode
├── schemas/
│   ├── auth.py           # Auth response models
│   ├── fitness.py        # Fitness response models
│   ├── user.py           # User/settings models
│   └── common.py         # Shared APIResponse model
└── utils/
    ├── logger.py          # Structured logger (env-aware)
    └── request_logger.py  # Request timing + X-Request-ID middleware
```

---

## Setup

### 1. Clone and create virtual environment

```powershell
git clone https://github.com/vinamra1102/stryder-backend
cd stryder-backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment

```powershell
Copy-Item .env.example .env
```

Edit `.env` and fill in:
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from [Google Cloud Console](https://console.cloud.google.com/)
- `SECRET_KEY` and `JWT_SECRET_KEY` — generate with:
  ```powershell
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

### 3. Google Cloud Console setup

1. Create a project → Enable **Google Fitness API**
2. OAuth consent screen → add scopes:
   - `openid`, `email`, `profile`
   - `https://www.googleapis.com/auth/fitness.activity.read`
3. Create OAuth 2.0 credentials (Web application)
4. Add authorised redirect URI: `http://localhost:8000/auth/callback`

### 4. Run

```powershell
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` (development only).

---

## API Endpoints

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Root ping |
| GET | `/health` | — | Status + environment |

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/auth/login` | — | Redirect to Google OAuth consent |
| GET | `/auth/callback` | — | OAuth callback → redirects to frontend with JWT |
| GET | `/auth/status` | JWT | Lightweight session check |
| GET | `/auth/me` | JWT | Current user profile |
| POST | `/auth/refresh` | JWT | Renew JWT + refresh Google access token |
| POST | `/auth/logout` | — | Client-side logout instruction |

### Fitness
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/fitness/steps/today` | JWT | Today's step count (UTC midnight → now) |
| GET | `/fitness/steps/week` | JWT | Last 7 calendar days |
| GET | `/fitness/steps/monthly?year=&month=` | JWT | Full calendar month (defaults to current) |
| GET | `/fitness/summary` | JWT | Dashboard summary: today + week + streak |
| GET | `/fitness/steps/history?from_date=&to_date=&limit=` | JWT | Custom date range (max 365 days) |

### User
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/user/settings` | JWT | Get app settings |
| PUT | `/user/settings` | JWT | Update app settings |

---

## Authentication Flow

```
Frontend → GET /auth/login
         ← 302 redirect to Google
         ← Google redirects to /auth/callback
         ← 302 redirect to FRONTEND_URL/auth/callback?token=<jwt>
Frontend stores JWT → sends as Authorization: Bearer <jwt> on all protected requests
```

---

## Known Limitations (pre-production)

| Limitation | Mitigation plan |
|-----------|-----------------|
| No database — settings not persisted | Add PostgreSQL + SQLAlchemy |
| Google access token embedded in JWT | Move to server-side token store (Redis) |
| No token denylist for logout | Add Redis-backed denylist |
| No rate limiting | Add slowapi or API gateway |
| No test suite | Add pytest + httpx test client |
