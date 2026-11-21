# Development Guide

## Environment Setup

### Prerequisites
- Python 3.11 or newer
- Node.js 20 LTS or newer
- Git

### Running an Application
Each project folder contains its own installation routines and instructions. To work with a specific application:

1. Navigate to the desired application directory:
   ```bash
   cd 01-data-visualization-dashboard
   ```
2. Configure the local environment variables by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Set up the backend virtual environment and dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
4. Run migrations and seed data:
   ```bash
   python -m database.seed
   ```
5. Launch the backend API:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
6. Set up and run the frontend:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

### Quality and Testing
Run tests within each project directory:
```bash
pytest tests/ -v
```
