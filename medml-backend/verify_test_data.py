#!/usr/bin/env python3
"""
Verification script to check the generated test data
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models import db, User, Patient, RiskPrediction

def verify_data():
    app = create_app('development')
    app_context = app.app_context()
    app_context.push()
    
    print("=" * 60)
    print("VERIFYING GENERATED TEST DATA")
    print("=" * 60)
    
    # Check counts
    admin_count = User.query.count()
    patient_count = Patient.query.count()
    prediction_count = RiskPrediction.query.count()
    
    print(f"Admin users: {admin_count}")
    print(f"Patients: {patient_count}")
    print(f"Risk predictions: {prediction_count}")
    
    # Check admin details
    admin = User.query.first()
    print(f"\nAdmin Details:")
    print(f"  Name: {admin.name}")
    print(f"  Email: {admin.email}")
    print(f"  Role: {admin.role}")
    
    # Check sample patients and their risk levels
    print(f"\nSample Patient Data (first 10 patients):")
    print("=" * 60)
    
    patients = Patient.query.limit(10).all()
    for i, patient in enumerate(patients, 1):
        pred = patient.risk_predictions.first()
        print(f"{i}. {patient.name}")
        print(f"   Age: {patient.age}, Gender: {patient.gender}, BMI: {patient.bmi:.1f}")
        print(f"   State: {patient.state_name}")
        if pred:
            print(f"   Diabetes Risk: {pred.diabetes_risk_level} ({pred.diabetes_risk_score:.2f})")
            print(f"   Heart Risk: {pred.heart_risk_level} ({pred.heart_risk_score:.2f})")
            print(f"   Liver Risk: {pred.liver_risk_level} ({pred.liver_risk_score:.2f})")
            print(f"   Mental Health Risk: {pred.mental_health_risk_level} ({pred.mental_health_risk_score:.2f})")
        print()
    
    # Check risk level distribution
    print("Risk Level Distribution:")
    print("=" * 30)
    
    diabetes_low = RiskPrediction.query.filter_by(diabetes_risk_level='Low').count()
    diabetes_medium = RiskPrediction.query.filter_by(diabetes_risk_level='Medium').count()
    diabetes_high = RiskPrediction.query.filter_by(diabetes_risk_level='High').count()
    
    heart_low = RiskPrediction.query.filter_by(heart_risk_level='Low').count()
    heart_medium = RiskPrediction.query.filter_by(heart_risk_level='Medium').count()
    heart_high = RiskPrediction.query.filter_by(heart_risk_level='High').count()
    
    liver_low = RiskPrediction.query.filter_by(liver_risk_level='Low').count()
    liver_medium = RiskPrediction.query.filter_by(liver_risk_level='Medium').count()
    liver_high = RiskPrediction.query.filter_by(liver_risk_level='High').count()
    
    mental_low = RiskPrediction.query.filter_by(mental_health_risk_level='Low').count()
    mental_medium = RiskPrediction.query.filter_by(mental_health_risk_level='Medium').count()
    mental_high = RiskPrediction.query.filter_by(mental_health_risk_level='High').count()
    
    print(f"Diabetes Risk Distribution:")
    print(f"  Low: {diabetes_low} ({diabetes_low/patient_count*100:.1f}%)")
    print(f"  Medium: {diabetes_medium} ({diabetes_medium/patient_count*100:.1f}%)")
    print(f"  High: {diabetes_high} ({diabetes_high/patient_count*100:.1f}%)")
    
    print(f"\nHeart Risk Distribution:")
    print(f"  Low: {heart_low} ({heart_low/patient_count*100:.1f}%)")
    print(f"  Medium: {heart_medium} ({heart_medium/patient_count*100:.1f}%)")
    print(f"  High: {heart_high} ({heart_high/patient_count*100:.1f}%)")
    
    print(f"\nLiver Risk Distribution:")
    print(f"  Low: {liver_low} ({liver_low/patient_count*100:.1f}%)")
    print(f"  Medium: {liver_medium} ({liver_medium/patient_count*100:.1f}%)")
    print(f"  High: {liver_high} ({liver_high/patient_count*100:.1f}%)")
    
    print(f"\nMental Health Risk Distribution:")
    print(f"  Low: {mental_low} ({mental_low/patient_count*100:.1f}%)")
    print(f"  Medium: {mental_medium} ({mental_medium/patient_count*100:.1f}%)")
    print(f"  High: {mental_high} ({mental_high/patient_count*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    verify_data()
