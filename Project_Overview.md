# PreventVance AI - Project Documentation

## 1. Introduction

**PreventVance AI** is a cutting-edge healthcare management system developed to bridge the gap in diagnostic accessibility, specifically designed for rural healthcare workers. In many underserved regions, the lack of immediate access to specialized diagnostics leads to delayed treatments and worsening health outcomes.

This project addresses this critical issue by deploying a robust AI-driven platform that enables **early detection and preventive care**. By leveraging machine learning models for multiple disease domains (Diabetes, Heart, Liver, and Mental Health), PreventVance AI empowers frontline health workers to screen patients effectively, identify risks before they become symptomatic, and provide actionable, personalized lifestyle recommendations.

## 2. Methodology

The system operates on a structured pipeline that transforms raw patient data into clinical insights:

### A. Data Collection & Input
Healthcare workers input patient demographics and clinical metrics (e.g., glucose levels, blood pressure, lipid profiles) via the **Streamlit** user interface. The forms are dynamic and tailored to specific disease assessments.

### B. Data Preprocessing & Feature Engineering
Before analysis, the raw data undergoes rigorous processing in the backend:
*   **Normalization**: Continuous variables are standardized.
*   **Feature Engineering**: The system automatically calculates derivative metrics such as *BMI*, *Diabetes Pedigree Function*, and metabolic interaction terms (e.g., `Age * BMI`). This ensures the input matches the complex feature space on which the models were trained.
*   **Encoding**: Categorical variables (e.g., Gender, Activity Level) are encoded into numerical formats.

### C. Predictive Modeling
The core intelligence engine utilizes an ensemble of specialized Machine Learning models stored in the `models_store`:
*   **Diabetes Prediction**: Utilizes **LightGBM** (with SMOTE for class balance) to analyze metabolic indicators.
*   **Heart Disease**: Deploys a tuned **SVM (Support Vector Machine)** to evaluate cardiovascular risk factors.
*   **Liver Disease**: Uses **LightGBM** to assess liver enzyme and protein levels.
*   **Mental Health**: Implements **Logistic Regression** to interpret psychometric scores (PHQ, GAD) for depression and anxiety risk.

### D. Generative AI Consultation
Once a risk profile is generated, the system integrates with **Google's Gemini 2.0 Flash API**. The AI analyzes the specific combination of risk factors (e.g., "High Blood Pressure" + "High Risk Diabetes") to generate a personalized, human-readable care plan covering diet, exercise, and sleep hygiene.

## 3. Technologies Used

The project is built on a modern, Python-centric stack ensuring performance and ease of deployment:

*   **Frontend**: `Streamlit` - For rapid development of interactive, data-centric web dashboards.
*   **Backend API**: `Flask` - A lightweight WSGI web application framework.
*   **Machine Learning**:
    *   `Scikit-Learn`: For model pipelining and SVMs.
    *   `LightGBM` & `XGBoost`: For high-performance gradient boosting models.
    *   `Joblib`: For efficient model serialization.
*   **Artificial Intelligence**: `Google Generative AI (Gemini 2.0 Flash)` - For natural language generation and personalized health advice.
*   **Database**: `SQLite` (Development) with `SQLAlchemy` ORM - For relational data management.
*   **Authentication**: `Flask-JWT-Extended` - For secure, token-based user authentication.
*   **Data Handling**: `Pandas` & `NumPy` - For high-performance data manipulation.

## 4. Potential Applications

While designed for rural healthcare, the modular architecture of PreventVance AI supports diverse use cases:

*   **Rural Health Centers (PHCs)**: Enabling auxiliary nurse midwives (ANMs) to conduct sophisticated screenings without immediate specialist supervision.
*   **Corporate Wellness Programs**: monitoring employee health trends to reduce insurance costs and improve workforce productivity.
*   **Telemedicine Platforms**: Serving as a triage tool to prioritize high-risk patients for remote doctor consultations.
*   **Community Health Camps**: Providing rapid mass-screenings in temporary setups where internet connectivity might be intermittent (core ML runs locally).
*   **Personal Health Journals**: Adapting the patient dashboard for individuals to track their own chronic conditions over time.
