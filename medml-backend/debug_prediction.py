#!/usr/bin/env python3
"""
Debug script to test prediction functionality for patient 62
"""

from app import create_app
from app.models import db, Patient
from app.services import run_prediction

def test_prediction():
    app = create_app()
    with app.app_context():
        patient = Patient.query.get(62)
        if not patient:
            print("❌ Patient 62 not found")
            return
            
        print(f"✅ Patient 62 found: {patient.name}")
        
        # Test each assessment type
        assessment_types = ['diabetes', 'liver', 'heart', 'mental_health']
        
        for assessment_type in assessment_types:
            print(f"\n--- Testing {assessment_type} prediction ---")
            try:
                # Get the latest features for this assessment type
                if assessment_type == 'diabetes':
                    data = patient.get_latest_diabetes_features()
                elif assessment_type == 'liver':
                    data = patient.get_latest_liver_features()
                elif assessment_type == 'heart':
                    data = patient.get_latest_heart_features()
                elif assessment_type == 'mental_health':
                    data = patient.get_latest_mental_health_features()
                
                print(f"✅ Got {assessment_type} data: {len(data)} features")
                print(f"Sample data: {dict(list(data.items())[:5])}")
                
                # Run prediction
                score = run_prediction(assessment_type, data)
                print(f"✅ {assessment_type} prediction successful: {score}")
                
            except Exception as e:
                print(f"❌ {assessment_type} prediction failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n--- Prediction Debug Summary ---")
        print("Check the logs above for details.")


if __name__ == "__main__":
    test_prediction()
