# Quickstart: Foundation & Project Initialization

**Feature**: 001-foundation-init
**Date**: 2025-12-30

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Version | Installation |
|------|---------|--------------|
| Python | 3.11+ | [python.org](https://python.org) |
| uv | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| npm | 10+ | Comes with Node.js |
| Git | Latest | [git-scm.com](https://git-scm.com) |

## Quick Start (5 minutes)

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd Phase_02
```

### 2. Start Backend

```bash
cd backend

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Start development server
uv run uvicorn src.main:app --reload --port 8000
```

Verify: Open http://localhost:8000/health - should return `{"status": "healthy", ...}`

### 3. Start Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Start development server
npm run dev
```

Verify: Open http://localhost:3000 - should show placeholder page

## Environment Variables

### Backend (.env)

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Database (placeholder - not used in foundation)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Authentication (placeholder - not used in foundation)
BETTER_AUTH_SECRET=your-secret-key-here
```

### Frontend (.env.local)

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication (placeholder - not used in foundation)
BETTER_AUTH_SECRET=your-secret-key-here
```

### Root (.env)

```env
# Shared across projects
BETTER_AUTH_SECRET=your-shared-secret-key-here
```

## Project Structure

```text
Phase_02/
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Environment loading
│   │   ├── database.py      # DB placeholder
│   │   └── middleware/
│   │       └── auth.py      # JWT placeholder
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx   # Root layout
│   │   │   └── page.tsx     # Home page
│   │   └── lib/
│   │       ├── auth.ts      # Auth placeholder
│   │       └── api.ts       # API client placeholder
│   ├── package.json
│   └── .env.example
│
├── CLAUDE.md                 # Project guidance
└── .gitignore
```

## Common Commands

### Backend

| Command | Description |
|---------|-------------|
| `uv sync` | Install dependencies |
| `uv run uvicorn src.main:app --reload` | Start dev server |
| `uv run pytest` | Run tests |
| `uv add <package>` | Add dependency |

### Frontend

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm run lint` | Run linter |
| `npm test` | Run tests |

## Verification Checklist

After setup, verify:

- [ ] Backend starts without errors
- [ ] `GET /health` returns 200
- [ ] Frontend starts without errors
- [ ] Placeholder page renders at http://localhost:3000
- [ ] No console errors in browser
- [ ] Environment files are created (not committed)

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # or :3000

# Kill process
kill -9 <PID>
```

### uv Not Found

```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### npm/Node Issues

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

After foundation is complete:

1. Run `/sp.tasks` to generate implementation tasks
2. Run `/sp.implement` to execute tasks
3. Proceed to Phase 2 (Authentication) specification
