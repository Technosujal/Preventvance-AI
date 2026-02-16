# Comprehensive Test Data Generator

## Overview
This test data generator creates realistic dummy data for intensive testing of the Healthcare App. It generates **1 admin user** and **50+ patients** with diverse health profiles and varying risk levels.

## Features

### User Data
- **1 Admin User**: Single healthcare administrator with credentials
- **50+ Patients**: Diverse demographics with realistic Indian names and locations

### Health/Risk Data
The generator creates realistic distributions across different risk levels:

#### Risk Level Distribution
- **Low Risk (40%)**: Younger users, healthy BMI, good lifestyle factors
- **Medium Risk (35%)**: Middle-aged users, moderate health indicators
- **High Risk (25%)**: Older users, elevated health markers, lifestyle factors

#### Disease-Specific Assessments
Each patient gets assessments for:
- **Diabetes**: Glucose levels, blood pressure, insulin, family history
- **Liver**: Bilirubin levels, enzyme markers, protein levels
- **Heart**: Cholesterol, blood pressure, lifestyle factors, family history
- **Mental Health**: PHQ-9, GAD-7 scores, depression/anxiety indicators

#### Risk Predictions
Automated risk scoring based on assessment data with realistic risk levels.

## Usage

### Running the Generator
```bash
cd medml-backend
python comprehensive_test_data_generator.py
```

### Verifying Generated Data
```bash
python verify_test_data.py
```

## Generated Data Summary

### Admin User
- **Email**: admin@healthcare.com
- **Password**: Admin123!
- **Role**: Chief Medical Officer

### Patients
- **Count**: 50 patients
- **Password**: Patient123! (for all patients)
- **Demographics**: Realistic age, gender, height, weight distributions
- **Locations**: Indian states and territories

### Risk Distributions (Sample Results)
- **Diabetes**: 70% Low, 0% Medium, 30% High
- **Heart**: 44% Low, 26% Medium, 30% High  
- **Liver**: 74% Low, 0% Medium, 26% High
- **Mental Health**: 48% Low, 14% Medium, 38% High

## Data Characteristics

### Low Risk Patients
- Age: 18-35 years
- BMI: < 25
- Normal lab values
- Healthy lifestyle indicators

### Medium Risk Patients  
- Age: 35-55 years
- BMI: 25-30
- Slightly elevated lab values
- Moderate lifestyle factors

### High Risk Patients
- Age: 50-80 years
- BMI: > 30
- Significantly elevated lab values
- Multiple risk factors

## Database Tables Populated
- `users` (1 admin)
- `patients` (50+ patients)
- `diabetes_assessments` (50 assessments)
- `liver_assessments` (50 assessments)
- `heart_assessments` (50 assessments)
- `mental_health_assessments` (50 assessments)
- `risk_predictions` (50 predictions)
- `consultations` (97 consultations)
- `consultation_notes` (47 notes)

## Notes
- The generator clears existing data before creating new data
- All passwords follow strong password requirements
- ABHA IDs are unique 14-digit numbers
- Risk scores are calculated based on realistic medical thresholds
- Consultations and notes are randomly distributed across patients
