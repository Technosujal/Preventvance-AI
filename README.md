# 🩺 PreventVance AI — Leading the Future of Early Health Defense

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Kaggle](https://img.shields.io/badge/Datasets-Kaggle-blue?logo=kaggle)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **PreventVance AI** is a comprehensive healthcare management system designed for **rural healthcare workers** to manage patient diagnostics and care delivery.  
> The system enables **early detection and preventive care** by identifying individuals at risk of diseases before they become symptomatic.

---
## 🧭 System Overview

**Project Goal:**  
Address critical gaps in diagnosis and treatment accessibility by enabling early detection and preventive care, particularly in underserved rural areas.

**Target Users:**
- **Primary:** Rural healthcare workers managing patient diagnostics and care delivery  
- **Secondary:** Corporate wellness programs seeking employee health monitoring solutions  

**Value Proposition:**  
Transform raw health data into actionable insights, enabling **preventive interventions** and **reducing long-term health complications**.

---
# PreventVance AI

Healthcare management system for early detection and preventive care.

## Overview
- Backend: Flask API (`/api/v1`) with JWT, rate limits, ML inference, PDF
- Frontend: Streamlit dashboards for admin and patient
- Database: SQLite (dev), migrations via Alembic; prod-ready for PostgreSQL/MySQL
- Models: XGBoost/LightGBM in `medml-backend/models_store`

## Quick Start (Windows)
- Run `start_system.bat`
- Open `http://localhost:8501`
- Admin login: `admin` / `Admin123!`

## Manual Setup
- Prerequisites: Python 3.8+, pip
- Install dependencies:
```
cd medml-backend && pip install -r requirements.txt
cd ../medml-frontend && pip install -r requirements.txt
```
- Initialize database and admin:
```
cd medml-backend

python create_admin.py

```
- Start services:
```
# Backend
python medml-backend/run.py

# Frontend (new terminal)
streamlit run medml-frontend/app.py --server.port 8501
```

## Configuration
- Copy `medml-backend/.env.example` to `medml-backend/.env` and set:
```
FLASK_ENV=development
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
DATABASE_URL=sqlite:///app/medml.db
SECRET_KEY=<secret>
JWT_SECRET_KEY=<jwt-secret>
GEMINI_API_KEY=<optional>
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501

RATELIMIT_DEFAULT_LIMITS=1000 per day;200 per hour;50 per minute
RATELIMIT_STORAGE_URI=memory://
RATELIMIT_ENABLED=true
USE_WAITRESS=false
```
- Frontend backend URL: `BACKEND_URL` or `st.secrets["backend_url"]` (default `http://127.0.0.1:5000/api/v1`).

## API Highlights
- Auth: `/auth/admin/login`, `/auth/patient/login`, refresh, logout
- Patients: create, list, view, update
- Assessments: diabetes, liver, heart, mental_health
- Predictions: trigger and fetch latest
- Reports: PDF generation
- Recommendations: Gemini AI (if configured)
- Health: `/health`

## Security
- JWT with token blocklist
- Bcrypt password hashing
- Role-based access (admin/patient)
- Rate limiting (`memory://`, `redis://`)
- CORS via env

## Testing
- Automated checks:
```
python tests/streamlit_frontend_checks.py
```
- Generate test data:
```
cd medml-backend
python comprehensive_test_data_generator.py
```
## Troubleshooting
- Clear rate limits:
```
cd medml-backend
python clear_rate_limits.py