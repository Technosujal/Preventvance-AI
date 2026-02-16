# How to Run the Healthcare App

## 🚀 Quick Start (Recommended)

### Option 1: Use the Batch File (Windows)

1. **Double-click `start_system.bat`** in the project root directory
2. This will automatically start both backend and frontend
3. Wait for both windows to open and initialize
4. Open your browser and go to: **http://localhost:8501**

### Option 2: Use the PowerShell Script (Windows)

1. **Right-click `start_system.ps1`** and select "Run with PowerShell"
2. This will automatically start both backend and frontend
3. Wait for both windows to open and initialize
4. Open your browser and go to: **http://localhost:8501**

## 📋 Prerequisites

Before running the application, ensure you have:

- **Python 3.8 or higher** installed
- **pip** package manager
- **Git** (for cloning the repository)
- **Windows 10/11** (for batch files) or any OS for manual setup

## 🛠️ Manual Startup (If batch files don't work)

### Step 1: Install Dependencies

```bash
# Install backend dependencies
cd medml-backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../medml-frontend
pip install -r requirements.txt
```

### Step 2: Initialize Database

```bash
cd ../medml-backend
python create_admin.py
```

### Step 3: Start Backend Server

Open Command Prompt or PowerShell and run:

```bash
cd medml-backend
python run.py
```

Wait for the message: "Running on http://127.0.0.1:5000"

### Step 4: Start Frontend (New Terminal)

Open a **new** Command Prompt or PowerShell window and run:

```bash
cd medml-frontend
streamlit run app.py
```

Wait for the message: "You can now view your Streamlit app in your browser."

### Step 5: Access the App

Open your browser and go to: **http://localhost:8501**

## 🔑 Authentication

Access to the system requires registration:

1. **Admin (Healthcare Worker)**: Register via the "Register" tab on the main landing page.
2. **Patient**: Can be registered by an Admin or self-register via the landing page.

### Login Access

- **Admin**: Use the username/email and password you registered with.
- **Patient**: Use your 14-digit ABHA ID and the password set during registration.

### Generate Test Data (Optional)

For comprehensive testing with 50+ patients:

```bash
cd medml-backend
python comprehensive_test_data_generator.py
```

## 🚨 Troubleshooting

### Quick Fixes

```bash
# Clear rate limits if getting 429 errors
cd medml-backend
python clear_rate_limits.py

# Recreate database if corrupted
python create_admin.py

# Check system status
python test_system.py
```

### If Backend Won't Start

1. **Check Python installation**: `python --version`
2. **Install dependencies**: `cd medml-backend && pip install -r requirements.txt`
3. **Check port availability**: `netstat -ano | findstr :5000`
4. **Kill process using port**: `taskkill /PID <PID_NUMBER> /F`
5. **Look for error messages** in the backend window

### If Frontend Won't Start

1. **Install Streamlit**: `pip install streamlit`
2. **Install frontend dependencies**: `cd medml-frontend && pip install -r requirements.txt`
3. **Check port availability**: `netstat -ano | findstr :8501`
4. **Look for error messages** in the frontend window

### If Login Fails

1. **Verify backend is running**: Check http://127.0.0.1:5000/api/v1/auth/me
2. **Check admin account exists**: Run `python create_admin.py`
3. **Verify credentials**: Use exact credentials from this guide
4. **Clear browser cache** and try again

### If ML Predictions Fail

1. **Check ML model files**: Verify files exist in `medml-backend/models_store/`
2. **Look for model loading errors** in backend logs
3. **This is normal if models are missing** - patient data will still be saved
4. **Required model files**:
   - `diabetes_XGBoost.pkl`
   - `heart_best_model.pkl`
   - `liver_LightGBM SMOTE.pkl`
   - `mental_health_depressiveness.pkl`

## 🧪 Testing the App

### Automated Testing

```bash
# System-wide tests
python test_system.py

# Frontend-specific tests
cd tests
python streamlit_frontend_checks.py
```

### Manual Testing

Follow comprehensive test cases in `run_manual_checks.md`:

1. **Admin login and dashboard access**
2. **Patient registration flow**
3. **Assessment completion**
4. **ML prediction triggering**
5. **Patient login and dashboard**
6. **PDF report generation**
7. **Error handling scenarios**

### Test Data Generation

Generate 50+ test patients for intensive testing:

```bash
cd medml-backend
python comprehensive_test_data_generator.py
python verify_test_data.py
```

## 💻 System Requirements

- **Python 3.8+** (required)
- **Windows 10/11** (for batch files) or any OS for manual setup
- **Web Browser** (Chrome, Firefox, Edge recommended)
- **8GB RAM** (recommended for ML models)
- **1GB free disk space** (for dependencies and database)
- **Internet connection** (for AI recommendations, optional)

## 🌐 URLs and Ports

- **Frontend**: http://localhost:8501 (Streamlit)
- **Backend API**: http://127.0.0.1:5000/api/v1
- **Backend Health Check**: http://127.0.0.1:5000/api/v1/auth/me
- **Backend Admin**: http://127.0.0.1:5000 (Flask development server)

## 📚 Additional Resources

- **Setup Guide**: `setup_frontend.md` - Detailed frontend configuration
- **Troubleshooting**: `TROUBLESHOOTING.md` - Comprehensive problem-solving guide
- **API Documentation**: `BACKEND_DISCOVERY.md` - Complete backend API reference
- **Test Cases**: `run_manual_checks.md` - Manual testing procedures
- **Test Data**: `medml-backend/TEST_DATA_GENERATOR_README.md` - Test data generation guide

## 🆘 Support

If you encounter issues:

1. **Check this troubleshooting section** above
2. **Look at error messages** in the command windows
3. **Verify all dependencies** are installed correctly
4. **Make sure both backend and frontend** are running
5. **Check the `TROUBLESHOOTING.md` file** for more detailed solutions
6. **Run system tests**: `python test_system.py` for diagnostics
