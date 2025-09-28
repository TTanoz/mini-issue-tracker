# Mini Issue Tracker (with Alembic)

A **FastAPI-based issue tracking system** featuring authentication, projects, issues, and comments.  
Now extended with **Alembic migrations** for database schema management.  
This repository includes a full pytest suite running against PostgreSQL (configured via `.env`).

---

## Project Layout

```
issue-tracker/
  alembic/               # Migration scripts
  alembic.ini            # Alembic config
  app/
    core/
      config.py
      security.py
    db/
      base.py
      session.py
    models/
      __init__.py
      user.py
      project.py
      issue.py
      comment.py
    routers/
      __init__.py
      auth.py
      users.py
      projects.py
      issues.py
      comments.py
    schemas/
      __init__.py
      auth.py
      comment.py
      issue.py
      project.py
      user.py
    deps.py
    main.py
    __init__.py
  tests/
    conftest.py
    test_auth.py
    test_comments.py
    test_issues.py
    test_projects.py
    test_users.py
  .env
  .gitignore
  pytest.ini
  requirements.txt
  README.md
```

> **Note:** `venv/`, `__pycache__/`, and `.pytest_cache/` are local-only and should be ignored by Git (see `.gitignore`).

---

## Tech Stack

- **FastAPI** (ASGI web framework)
- **SQLAlchemy 2.0** (ORM)
- **Pydantic v2** (validation & serialization)
- **PostgreSQL** (development & tests)
- **Alembic** (migrations)
- **Pytest** (test runner)

---

## Setup

### 1) Clone

```bash
git clone https://github.com/TTanoz/mini-issue-tracker.git
cd mini-issue-tracker
```

### 2) Create & activate virtualenv

**Windows (PowerShell):**
```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment

Use the example file to create your local `.env`:

```ini
# .env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/mini_issue_tracker
TEST_DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/mini_issue_tracker_test
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> Make sure the PostgreSQL databases exist (create them if not):
> ```sql
> CREATE DATABASE mini_issue_tracker;
> CREATE DATABASE mini_issue_tracker_test;
> ```

---

## Run Database Migrations (Alembic)

Initialize migrations (already in repo):

```bash
alembic upgrade head
```

Create new revision when schema changes:

```bash
alembic revision --autogenerate -m "add new field"
alembic upgrade head
```

Rollback:

```bash
alembic downgrade -1
```

---

## Run the App

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Docs (Swagger): http://127.0.0.1:8000/docs

---

## API Overview

### Auth
- `POST /auth/register` – create user
- `POST /auth/login` – obtain JWT

### Users
- `GET /users/me` – current user
- `POST /users/me/change-password` – change password
- `GET /users` – list users (auth required)
- `GET /users/{user_id}` – user detail (auth required)

### Projects
- `POST /projects` – create
- `GET /projects` – list
- `GET /projects/{project_id}` – detail
- `DELETE /projects/{project_id}` – delete (owner only)

### Issues
- `POST /projects/{project_id}/issues` – create
- `GET /projects/{project_id}/issues` – list (by project)
- `GET /issues/{issue_id}` – detail
- `PATCH /issues/{issue_id}` – update (reporter only)
- `DELETE /issues/{issue_id}` – delete (reporter only)

### Comments
- `POST /issues/{issue_id}/comments` – create
- `GET /issues/{issue_id}/comments` – list (by issue)
- `GET /comments/{comment_id}` – detail
- `PATCH /comments/{comment_id}` – update (author only)
- `DELETE /comments/{comment_id}` – delete (author only)

---

## Running Tests

1. Ensure `TEST_DATABASE_URL` is set in `.env` and the database exists.
2. Run:
```bash
pytest -v
```

Pytest is configured to use **PostgreSQL** via `tests/conftest.py`; tables are created/dropped around each test, keeping tests isolated.

---

## License

This project is for **educational purposes** only.
