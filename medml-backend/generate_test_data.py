#!/usr/bin/env python3
"""
Comprehensive Test Data Generator for Healthcare App
Generates realistic dummy data with varying risk levels for intensive testing.
Creates 50+ admin users and 30+ patients with diverse health profiles.
"""

import os
import sys
import random
import string
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models import db, User, Patient, DiabetesAssessment, LiverAssessment, HeartAssessment, MentalHealthAssessment, RiskPrediction, Consultation, ConsultationNote
from app.db_seeder import seed_static_recommendations

# Initialize Faker for realistic data generation
fake = Faker()

class TestDataGenerator:
    def __init__(self):
        self.app = create_app('development')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Risk level distributions (realistic healthcare distribution)
        self.risk_distribution = {
            'low': 0.4,      # 40% low risk
            'medium': 0.35,  # 35% medium risk  
            'high': 0.25     # 25% high risk
        }
        
        # Indian states for realistic data
        self.indian_states = [
            'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal',
            'Gujarat', 'Rajasthan', 'Madhya Pradesh', 'Kerala', 'Andhra Pradesh',
            'Telangana', 'Odisha', 'Bihar', 'Punjab', 'Haryana', 'Delhi',
            'Jammu and Kashmir', 'Himachal Pradesh', 'Uttarakhand', 'Assam',
            'Manipur', 'Meghalaya', 'Nagaland', 'Tripura', 'Sikkim',
            'Arunachal Pradesh', 'Mizoram', 'Goa', 'Chhattisgarh', 'Jharkhand'
        ]
        
        # Healthcare facilities
        self.facilities = [
            'Apollo Hospitals', 'Fortis Healthcare', 'Max Healthcare', 'Manipal Hospitals',
            'Narayana Health', 'Columbia Asia', 'KIMS Hospitals', 'Medanta',
            'AIIMS', 'PGI Chandigarh', 'CMC Vellore', 'Tata Memorial Hospital',
            'Rajiv Gandhi Cancer Institute', 'Sankara Eye Care', 'LV Prasad Eye Institute',
            'NIMHANS', 'NIMHANS Bangalore', 'Christian Medical College',
            'JIPMER Puducherry', 'SGPGI Lucknow', 'Regional Cancer Centre',
            'Kidwai Memorial Institute', 'Cancer Institute Chennai',
            'Regional Institute of Medical Sciences', 'Gandhi Medical College',
            'Osmania Medical College', 'Bangalore Medical College',
            'Government Medical College', 'Private Medical College',
            'District Hospital', 'Community Health Centre'
        ]
        
        # Designations for healthcare workers
        self.designations = [
            'Doctor', 'Nurse', 'Administrator', 'Medical Officer', 'Senior Doctor',
            'Chief Medical Officer', 'Head Nurse', 'Medical Superintendent',
            'Clinical Coordinator', 'Health Manager', 'Medical Director',
            'Senior Medical Officer', 'Junior Doctor', 'Staff Nurse',
            'Nursing Supervisor', 'Medical Assistant', 'Health Coordinator'
        ]

    def generate_abha_id(self):
        """Generate a realistic ABHA ID (14 digits)"""
        return ''.join([str(random.randint(0, 9)) for _ in range(14)])

    def calculate_bmi(self, height, weight):
        """Calculate BMI from height (cm) and weight (kg)"""
        height_m = height / 100
        return weight / (height_m ** 2)

    def get_risk_level(self):
        """Get risk level based on distribution"""
        rand = random.random()
        cumulative = 0
        for level, prob in self.risk_distribution.items():
            cumulative += prob
            if rand <= cumulative:
                return level
        return 'medium'

    def generate_users(self, count=50):
        """Generate admin users (healthcare workers)"""
        print(f"Generating {count} admin users...")
        
        users = []
        for i in range(count):
            # Ensure unique email and username
            email = fake.email()
            username = fake.user_name()
            
            # Check for uniqueness
            while User.query.filter_by(email=email).first():
                email = fake.email()
            while User.query.filter_by(username=username).first():
                username = fake.user_name()
            
            user = User(
                name=fake.name(),
                email=email,
                username=username,
                designation=random.choice(self.designations),
                contact_number=fake.phone_number()[:15],  # Limit length
                facility_name=random.choice(self.facilities),
                role='admin'
            )
            user.set_password('admin123')  # Default password for testing
            
            users.append(user)
        
        db.session.add_all(users)
        db.session.commit()
        print(f"✓ Generated {len(users)} admin users")
        return users

    def generate_patients(self, count=30, users=None):
        """Generate patients with realistic demographics"""
        print(f"Generating {count} patients...")
        
        if not users:
            users = User.query.all()
        
        patients = []
        used_abha_ids = set()
        
        for i in range(count):
            # Generate unique ABHA ID
            abha_id = self.generate_abha_id()
            while abha_id in used_abha_ids:
                abha_id = self.generate_abha_id()
            used_abha_ids.add(abha_id)
            
            # Generate realistic demographics
            age = random.randint(18, 80)
            gender = random.choice(['Male', 'Female', 'Other'])
            
            # Height and weight based on age and gender
            if gender == 'Male':
                height = random.uniform(160, 190)  # cm
                weight = random.uniform(50, 100)   # kg
            else:
                height = random.uniform(150, 175)  # cm
                weight = random.uniform(40, 85)    # kg
            
            patient = Patient(
                name=fake.name(),
                age=age,
                gender=gender,
                height=round(height, 1),
                weight=round(weight, 1),
                abha_id=abha_id,
                state_name=random.choice(self.indian_states),
                created_by_admin_id=random.choice(users).id
            )
            patient.set_password('patient123')  # Default password for testing
            
            patients.append(patient)
        
        db.session.add_all(patients)
        db.session.commit()
        print(f"✓ Generated {len(patients)} patients")
        return patients

    def generate_diabetes_assessments(self, patients):
        """Generate diabetes assessments with realistic risk patterns"""
        print("Generating diabetes assessments...")
        
        assessments = []
        for patient in patients:
            risk_level = self.get_risk_level()
            
            # Generate assessment data based on risk level
            if risk_level == 'low':
                # Low risk: younger, healthy BMI, good lifestyle
                glucose = random.uniform(70, 100)
                blood_pressure = random.uniform(80, 120)
                skin_thickness = random.uniform(10, 25)
                insulin = random.uniform(5, 25)
                diabetes_history = random.choice([False, False, False, True])  # 25% chance
                pregnancy = random.choice([False, False, False, True]) if patient.gender == 'Female' else False
                
            elif risk_level == 'medium':
                # Medium risk: middle-aged, slightly elevated values
                glucose = random.uniform(100, 125)
                blood_pressure = random.uniform(120, 140)
                skin_thickness = random.uniform(25, 35)
                insulin = random.uniform(25, 50)
                diabetes_history = random.choice([False, False, True, True])  # 50% chance
                pregnancy = random.choice([False, False, True, True]) if patient.gender == 'Female' else False
                
            else:  # high risk
                # High risk: older, elevated values, poor lifestyle
                glucose = random.uniform(125, 200)
                blood_pressure = random.uniform(140, 180)
                skin_thickness = random.uniform(35, 50)
                insulin = random.uniform(50, 100)
                diabetes_history = random.choice([False, True, True, True])  # 75% chance
                pregnancy = random.choice([False, True, True, True]) if patient.gender == 'Female' else False
            
            assessment = DiabetesAssessment(
                patient_id=patient.id,
                pregnancy=pregnancy,
                glucose=round(glucose, 1),
                blood_pressure=round(blood_pressure, 1),
                skin_thickness=round(skin_thickness, 1),
                insulin=round(insulin, 1),
                diabetes_history=diabetes_history
            )
            assessments.append(assessment)
        
        db.session.add_all(assessments)
        db.session.commit()
        print(f"✓ Generated {len(assessments)} diabetes assessments")

    def generate_liver_assessments(self, patients):
        """Generate liver assessments with realistic risk patterns"""
        print("Generating liver assessments...")
        
        assessments = []
        for patient in patients:
            risk_level = self.get_risk_level()
            
            # Generate assessment data based on risk level
            if risk_level == 'low':
                # Low risk: normal liver function
                total_bilirubin = random.uniform(0.3, 1.2)
                direct_bilirubin = random.uniform(0.1, 0.3)
                alkaline_phosphatase = random.uniform(44, 147)
                sgpt_alamine_aminotransferase = random.uniform(7, 56)
                sgot_aspartate_aminotransferase = random.uniform(10, 40)
                total_protein = random.uniform(6.0, 8.3)
                albumin = random.uniform(3.5, 5.0)
                
            elif risk_level == 'medium':
                # Medium risk: slightly elevated values
                total_bilirubin = random.uniform(1.2, 2.0)
                direct_bilirubin = random.uniform(0.3, 0.6)
                alkaline_phosphatase = random.uniform(147, 200)
                sgpt_alamine_aminotransferase = random.uniform(56, 100)
                sgot_aspartate_aminotransferase = random.uniform(40, 80)
                total_protein = random.uniform(5.5, 6.0)
                albumin = random.uniform(3.0, 3.5)
                
            else:  # high risk
                # High risk: significantly elevated values
                total_bilirubin = random.uniform(2.0, 5.0)
                direct_bilirubin = random.uniform(0.6, 2.0)
                alkaline_phosphatase = random.uniform(200, 400)
                sgpt_alamine_aminotransferase = random.uniform(100, 300)
                sgot_aspartate_aminotransferase = random.uniform(80, 200)
                total_protein = random.uniform(4.5, 5.5)
                albumin = random.uniform(2.0, 3.0)
            
            assessment = LiverAssessment(
                patient_id=patient.id,
                total_bilirubin=round(total_bilirubin, 1),
                direct_bilirubin=round(direct_bilirubin, 1),
                alkaline_phosphatase=round(alkaline_phosphatase, 1),
                sgpt_alamine_aminotransferase=round(sgpt_alamine_aminotransferase, 1),
                sgot_aspartate_aminotransferase=round(sgot_aspartate_aminotransferase, 1),
                total_protein=round(total_protein, 1),
                albumin=round(albumin, 1)
            )
            assessments.append(assessment)
        
        db.session.add_all(assessments)
        db.session.commit()
        print(f"✓ Generated {len(assessments)} liver assessments")

    def generate_heart_assessments(self, patients):
        """Generate heart assessments with realistic risk patterns"""
        print("Generating heart assessments...")
        
        assessments = []
        for patient in patients:
            risk_level = self.get_risk_level()
            
            # Generate assessment data based on risk level
            if risk_level == 'low':
                # Low risk: healthy cardiovascular profile
                cholesterol_level = random.uniform(150, 200)
                systolic_bp = random.randint(110, 130)
                diastolic_bp = random.randint(70, 85)
                diabetes = random.choice([False, False, False, True])  # 25% chance
                hypertension = random.choice([False, False, False, True])  # 25% chance
                smoking = random.choice([False, False, False, True])  # 25% chance
                physical_activity = random.choice([True, True, True, False])  # 75% chance
                diet_score = random.randint(7, 10)
                
            elif risk_level == 'medium':
                # Medium risk: moderate cardiovascular risk
                cholesterol_level = random.uniform(200, 250)
                systolic_bp = random.randint(130, 150)
                diastolic_bp = random.randint(85, 95)
                diabetes = random.choice([False, False, True, True])  # 50% chance
                hypertension = random.choice([False, False, True, True])  # 50% chance
                smoking = random.choice([False, False, True, True])  # 50% chance
                physical_activity = random.choice([True, True, False, False])  # 50% chance
                diet_score = random.randint(4, 7)
                
            else:  # high risk
                # High risk: high cardiovascular risk
                cholesterol_level = random.uniform(250, 350)
                systolic_bp = random.randint(150, 180)
                diastolic_bp = random.randint(95, 110)
                diabetes = random.choice([False, True, True, True])  # 75% chance
                hypertension = random.choice([False, True, True, True])  # 75% chance
                smoking = random.choice([False, True, True, True])  # 75% chance
                physical_activity = random.choice([True, False, False, False])  # 25% chance
                diet_score = random.randint(1, 4)
            
            assessment = HeartAssessment(
                patient_id=patient.id,
                diabetes=diabetes,
                hypertension=hypertension,
                obesity=self.calculate_bmi(patient.height, patient.weight) > 30,
                smoking=smoking,
                alcohol_consumption=random.choice([False, False, False, True]) if risk_level == 'low' else random.choice([False, True, True, True]),
                physical_activity=physical_activity,
                diet_score=diet_score,
                cholesterol_level=round(cholesterol_level, 1),
                triglyceride_level=round(random.uniform(100, 300), 1),
                ldl_level=round(random.uniform(100, 200), 1),
                hdl_level=round(random.uniform(30, 80), 1),
                systolic_bp=systolic_bp,
                diastolic_bp=diastolic_bp,
                air_pollution_exposure=round(random.uniform(10, 100), 1),
                family_history=random.choice([False, False, False, True]) if risk_level == 'low' else random.choice([False, True, True, True]),
                stress_level=random.randint(1, 5) if risk_level == 'low' else random.randint(6, 10),
                heart_attack_history=random.choice([False, False, False, True]) if risk_level == 'low' else random.choice([False, True, True, True])
            )
            assessments.append(assessment)
        
        db.session.add_all(assessments)
        db.session.commit()
        print(f"✓ Generated {len(assessments)} heart assessments")

    def generate_mental_health_assessments(self, patients):
        """Generate mental health assessments with realistic risk patterns"""
        print("Generating mental health assessments...")
        
        assessments = []
        for patient in patients:
            risk_level = self.get_risk_level()
            
            # Generate assessment data based on risk level
            if risk_level == 'low':
                # Low risk: good mental health indicators
                phq_score = random.randint(0, 4)  # PHQ-9 depression score
                gad_score = random.randint(0, 4)  # GAD-7 anxiety score
                depressiveness = random.choice([False, False, False, True])  # 25% chance
                suicidal = random.choice([False, False, False, False])  # Very low chance
                anxiousness = random.choice([False, False, False, True])  # 25% chance
                sleepiness = random.choice([False, False, False, True])  # 25% chance
                
            elif risk_level == 'medium':
                # Medium risk: moderate mental health concerns
                phq_score = random.randint(4, 7)
                gad_score = random.randint(4, 7)
                depressiveness = random.choice([False, False, True, True])  # 50% chance
                suicidal = random.choice([False, False, False, True])  # Low chance
                anxiousness = random.choice([False, False, True, True])  # 50% chance
                sleepiness = random.choice([False, False, True, True])  # 50% chance
                
            else:  # high risk
                # High risk: significant mental health concerns
                phq_score = random.randint(7, 15)
                gad_score = random.randint(7, 15)
                depressiveness = random.choice([False, True, True, True])  # 75% chance
                suicidal = random.choice([False, False, True, True])  # Higher chance
                anxiousness = random.choice([False, True, True, True])  # 75% chance
                sleepiness = random.choice([False, True, True, True])  # 75% chance
            
            assessment = MentalHealthAssessment(
                patient_id=patient.id,
                phq_score=phq_score,
                gad_score=gad_score,
                depressiveness=depressiveness,
                suicidal=suicidal,
                anxiousness=anxiousness,
                sleepiness=sleepiness
            )
            assessments.append(assessment)
        
        db.session.add_all(assessments)
        db.session.commit()
        print(f"✓ Generated {len(assessments)} mental health assessments")

    def generate_risk_predictions(self, patients):
        """Generate risk predictions based on assessment data"""
        print("Generating risk predictions...")
        
        predictions = []
        for patient in patients:
            # Get latest assessments
            diabetes_assessment = patient.diabetes_assessments.first()
            liver_assessment = patient.liver_assessments.first()
            heart_assessment = patient.heart_assessments.first()
            mental_health_assessment = patient.mental_health_assessments.first()
            
            prediction = RiskPrediction(patient_id=patient.id)
            
            # Generate risk scores based on assessment data
            if diabetes_assessment:
                # Calculate diabetes risk score based on assessment
                risk_factors = 0
                if diabetes_assessment.glucose > 125: risk_factors += 0.3
                if diabetes_assessment.blood_pressure > 140: risk_factors += 0.2
                if diabetes_assessment.insulin > 50: risk_factors += 0.2
                if diabetes_assessment.diabetes_history: risk_factors += 0.2
                if patient.bmi > 30: risk_factors += 0.1
                
                diabetes_score = min(risk_factors, 1.0)
                prediction.update_risk('diabetes', diabetes_score, '1.0')
            
            if liver_assessment:
                # Calculate liver risk score based on assessment
                risk_factors = 0
                if liver_assessment.sgpt_alamine_aminotransferase > 100: risk_factors += 0.3
                if liver_assessment.sgot_aspartate_aminotransferase > 80: risk_factors += 0.3
                if liver_assessment.total_bilirubin > 2.0: risk_factors += 0.2
                if liver_assessment.albumin < 3.0: risk_factors += 0.2
                
                liver_score = min(risk_factors, 1.0)
                prediction.update_risk('liver', liver_score, '1.0')
            
            if heart_assessment:
                # Calculate heart risk score based on assessment
                risk_factors = 0
                if heart_assessment.diabetes: risk_factors += 0.2
                if heart_assessment.hypertension: risk_factors += 0.2
                if heart_assessment.smoking: risk_factors += 0.2
                if heart_assessment.cholesterol_level > 250: risk_factors += 0.2
                if heart_assessment.systolic_bp > 150: risk_factors += 0.2
                if heart_assessment.family_history: risk_factors += 0.1
                if heart_assessment.physical_activity == False: risk_factors += 0.1
                
                heart_score = min(risk_factors, 1.0)
                prediction.update_risk('heart', heart_score, '1.0')
            
            if mental_health_assessment:
                # Calculate mental health risk score based on assessment
                risk_factors = 0
                if mental_health_assessment.phq_score > 7: risk_factors += 0.3
                if mental_health_assessment.gad_score > 7: risk_factors += 0.3
                if mental_health_assessment.depressiveness: risk_factors += 0.2
                if mental_health_assessment.anxiousness: risk_factors += 0.2
                if mental_health_assessment.suicidal: risk_factors += 0.3
                
                mental_health_score = min(risk_factors, 1.0)
                prediction.update_risk('mental_health', mental_health_score, '1.0')
            
            predictions.append(prediction)
        
        db.session.add_all(predictions)
        db.session.commit()
        print(f"✓ Generated {len(predictions)} risk predictions")

    def generate_consultations(self, patients, users):
        """Generate consultation bookings for patients"""
        print("Generating consultations...")
        
        consultations = []
        diseases = ['diabetes', 'liver', 'heart', 'mental_health']
        consultation_types = ['teleconsultation', 'in_person']
        statuses = ['Booked', 'Completed', 'Cancelled']
        
        for patient in patients:
            # Generate 1-3 consultations per patient
            num_consultations = random.randint(1, 3)
            
            for _ in range(num_consultations):
                consultation_datetime = fake.date_time_between(
                    start_date='-30d', 
                    end_date='+30d'
                )
                
                consultation = Consultation(
                    patient_id=patient.id,
                    admin_id=random.choice(users).id,
                    disease=random.choice(diseases),
                    consultation_type=random.choice(consultation_types),
                    consultation_datetime=consultation_datetime,
                    notes=fake.text(max_nb_chars=200) if random.random() > 0.5 else None,
                    status=random.choice(statuses)
                )
                consultations.append(consultation)
        
        db.session.add_all(consultations)
        db.session.commit()
        print(f"✓ Generated {len(consultations)} consultations")

    def generate_consultation_notes(self, patients, users):
        """Generate consultation notes for patients"""
        print("Generating consultation notes...")
        
        notes = []
        
        for patient in patients:
            # Generate 0-2 notes per patient
            num_notes = random.randint(0, 2)
            
            for _ in range(num_notes):
                note = ConsultationNote(
                    patient_id=patient.id,
                    admin_id=random.choice(users).id,
                    notes=fake.text(max_nb_chars=500)
                )
                notes.append(note)
        
        db.session.add_all(notes)
        db.session.commit()
        print(f"✓ Generated {len(notes)} consultation notes")

    def generate_all_data(self, user_count=55, patient_count=35):
        """Generate all test data"""
        print("=" * 60)
        print("HEALTHCARE APP TEST DATA GENERATOR")
        print("=" * 60)
        
        try:
            # Clear existing data (optional - comment out if you want to keep existing data)
            print("Clearing existing data...")
            db.drop_all()
            db.create_all()
            
            # Seed static recommendations
            seed_static_recommendations()
            
            # Generate users (55 admin users as requested)
            users = self.generate_users(user_count)
            
            # Generate patients (35 patients as requested)
            patients = self.generate_patients(patient_count, users)
            
            # Generate assessments
            self.generate_diabetes_assessments(patients)
            self.generate_liver_assessments(patients)
            self.generate_heart_assessments(patients)
            self.generate_mental_health_assessments(patients)
            
            # Generate risk predictions
            self.generate_risk_predictions(patients)
            
            # Generate consultations and notes
            self.generate_consultations(patients, users)
            self.generate_consultation_notes(patients, users)
            
            print("\n" + "=" * 60)
            print("DATA GENERATION COMPLETE!")
            print("=" * 60)
            print(f"✓ Generated {len(users)} admin users")
            print(f"✓ Generated {len(patients)} patients")
            print(f"✓ Generated assessments for all patients")
            print(f"✓ Generated risk predictions for all patients")
            print(f"✓ Generated consultations and notes")
            print("\nRisk Level Distribution:")
            print(f"  Low Risk: 40% of patients")
            print(f"  Medium Risk: 35% of patients")
            print(f"  High Risk: 25% of patients")
            print("\nDefault passwords:")
            print("  Admin users: admin123")
            print("  Patients: patient123")
            print("\nDatabase populated successfully!")
            
        except Exception as e:
            print(f"Error generating data: {e}")
            db.session.rollback()
            raise

    def __del__(self):
        """Clean up app context"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

def main():
    """Main function to run the data generator"""
    generator = TestDataGenerator()
    
    # Generate 55+ admin users and 35+ patients as requested
    user_count = 55      # Number of admin users (exceeds 50+ requirement)
    patient_count = 35   # Number of patients (exceeds 30+ requirement)
    
    generator.generate_all_data(user_count, patient_count)

if __name__ == '__main__':
    main()
