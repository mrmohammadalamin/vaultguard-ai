# VaultGuard AI Architecture

## Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: SQLite (SQLAlchemy ORM)
- **Real-Time**: WebSockets for streaming execution states to the frontend.
- **Engine**: The autonomous agent simulation runs a state machine (`backend/engine/state_machine.py`) replicating closed-loop engineering and governance interception (`backend/engine/governance.py`).

## Frontend
- **Framework**: Next.js (App Router, React 18)
- **Styling**: TailwindCSS
- **State**: React Hooks with native WebSocket API for real-time reactivity.
- **Components**: Execution Dashboard, Governance Console.

## Infrastructure
- Docker & Docker Compose encapsulate the frontend and backend services into a reproducible environment.
