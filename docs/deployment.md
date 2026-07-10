# VaultGuard AI Deployment

## Docker Environment
Ensure Docker and Docker Compose are installed.
1. Build the images:
   ```bash
   docker-compose build
   ```
2. Start the services:
   ```bash
   docker-compose up -d
   ```
3. Stop the services:
   ```bash
   docker-compose down
   ```

## Manual Deployment
### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
