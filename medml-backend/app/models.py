# HealthCare App/medml-backend/app/models.py
from app.extensions import db, bcrypt
from datetime import datetime
from flask import current_app
import mongoengine as me


class User(db.Document):
    """
    Represents an Admin user (Healthcare Worker)
    """
    meta = {'collection': 'users'}
    
    name = me.StringField(max_length=150, required=True)
    email = me.StringField(max_length=120, unique=True, required=True)
    username = me.StringField(max_length=80, unique=True, sparse=True)
    password_hash = me.StringField(max_length=256, required=True)
    designation = me.StringField(max_length=100)
    contact_number = me.StringField(max_length=20)
    facility_name = me.StringField(max_length=150)
    role = me.StringField(max_length=20, default='admin')
    created_at = me.DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "designation": self.designation,
            "contact_number": self.contact_number,
            "facility_name": self.facility_name,
            "role": self.role,
            "joined_at": self.created_at.isoformat() if self.created_at else None
        }

class Patient(db.Document):
    """
    Represents a Patient
    """
    meta = {'collection': 'patients'}
    
    name = me.StringField(max_length=150, required=True)
    age = me.IntField(required=True)
    gender = me.StringField(max_length=20, required=True)
    height = me.FloatField(required=True)
    weight = me.FloatField(required=True)
    abha_id = me.StringField(max_length=14, unique=True, required=True)
    password_hash = me.StringField(max_length=256, required=True)
    state_name = me.StringField(max_length=100)
    
    created_by_admin_id = me.ReferenceField('User', reverse_delete_rule=me.NULLIFY)
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def bmi(self):
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100.0
            return round(self.weight / (height_m ** 2), 2)
        return None

    def to_dict(self, include_admin=True, include_history=False, include_latest_prediction=False, include_notes=False):
        data = {
            "patient_id": str(self.id),
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "abha_id": self.abha_id,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "state_name": self.state_name,
            "created_by_admin_id": str(self.created_by_admin_id.pk) if self.created_by_admin_id else None,
            "created_at": self.created_at.isoformat(),
        }
        if include_admin and self.created_by_admin_id:
            data['created_by_admin'] = self.created_by_admin_id.to_dict()
            
        if include_history:
            data['diabetes_assessments'] = [a.to_dict() for a in DiabetesAssessment.objects(patient_id=self).order_by('-assessed_at')]
            data['liver_assessments'] = [a.to_dict() for a in LiverAssessment.objects(patient_id=self).order_by('-assessed_at')]
            data['heart_assessments'] = [a.to_dict() for a in HeartAssessment.objects(patient_id=self).order_by('-assessed_at')]
            data['mental_health_assessments'] = [a.to_dict() for a in MentalHealthAssessment.objects(patient_id=self).order_by('-assessed_at')]
            data['risk_predictions'] = [p.to_dict() for p in RiskPrediction.objects(patient_id=self).order_by('-predicted_at')]
        
        if include_latest_prediction:
             latest = RiskPrediction.objects(patient_id=self).order_by('-predicted_at').first()
             data['latest_prediction'] = latest.to_dict() if latest else None

        if include_notes:
            data['consultation_notes'] = [n.to_dict() for n in ConsultationNote.objects(patient_id=self).order_by('-created_at')]
            
        return data

    def _get_common_features(self):
        return {
            "age": self.age,
            "gender": self.gender,
            "bmi": self.bmi
        }

    def get_latest_diabetes_features(self):
        latest_assessment = DiabetesAssessment.objects(patient_id=self).order_by('-assessed_at').first()
        if not latest_assessment:
            raise ValueError("No diabetes assessment found for patient")
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features

    def get_latest_liver_features(self):
        latest_assessment = LiverAssessment.objects(patient_id=self).order_by('-assessed_at').first()
        if not latest_assessment:
            raise ValueError("No liver assessment found for patient")
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features

    def get_latest_heart_features(self):
        latest_assessment = HeartAssessment.objects(patient_id=self).order_by('-assessed_at').first()
        if not latest_assessment:
            raise ValueError("No heart assessment found for patient")
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features

    def get_latest_mental_health_features(self):
        latest_assessment = MentalHealthAssessment.objects(patient_id=self).order_by('-assessed_at').first()
        if not latest_assessment:
            raise ValueError("No mental health assessment found for patient")
        features = latest_assessment.to_dict(include_patient_data=True)
        features.update(self._get_common_features())
        return features


class DoctorAvailability(db.Document):
    """
    Working hours/availability for a doctor on specific days of the week.
    """
    meta = {'collection': 'doctor_availabilities'}
    doctor_id = me.ReferenceField('User', required=True)
    day_of_week = me.IntField(required=True) # 0=Monday, 6=Sunday
    start_time = me.StringField(max_length=5, required=True) # "HH:MM" format
    end_time = me.StringField(max_length=5, required=True) # "HH:MM" format
    slot_duration = me.IntField(default=30) # in minutes


    def to_dict(self):
        return {
            "day_of_week": self.day_of_week,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "slot_duration": self.slot_duration
        }

# Extending User to include availability if needed
# User.availabilities = me.EmbeddedDocumentListField(DoctorAvailability)

class DiabetesAssessment(db.Document):
    meta = {'collection': 'diabetes_assessments'}
    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    assessed_by_admin_id = me.ReferenceField('User', reverse_delete_rule=me.NULLIFY)
    assessed_at = me.DateTimeField(default=datetime.utcnow)
    
    pregnancy = me.BooleanField(default=False)
    glucose = me.FloatField(required=True)
    blood_pressure = me.FloatField(required=True)
    skin_thickness = me.FloatField(required=True)
    insulin = me.FloatField(required=True)
    diabetes_history = me.BooleanField(default=False)

    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "pregnancy": self.pregnancy,
            "glucose": self.glucose,
            "blood_pressure": self.blood_pressure,
            "skin_thickness": self.skin_thickness,
            "insulin": self.insulin,
            "diabetes_history": self.diabetes_history,
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient_id:
             data.update(self.patient_id._get_common_features())
        return data

class LiverAssessment(db.Document):
    meta = {'collection': 'liver_assessments'}
    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    assessed_by_admin_id = me.ReferenceField('User', reverse_delete_rule=me.NULLIFY)
    assessed_at = me.DateTimeField(default=datetime.utcnow)
    
    total_bilirubin = me.FloatField(required=True)
    direct_bilirubin = me.FloatField(required=True)
    alkaline_phosphatase = me.FloatField(required=True)
    sgpt_alamine_aminotransferase = me.FloatField(required=True)
    sgot_aspartate_aminotransferase = me.FloatField(required=True)
    total_protein = me.FloatField(required=True)
    albumin = me.FloatField(required=True)
    
    @property
    def ag_ratio(self):
        if self.albumin and self.total_protein and self.total_protein > self.albumin:
            globulin = self.total_protein - self.albumin
            if globulin > 0:
                return round(self.albumin / globulin, 2)
        return None

    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "total_bilirubin": self.total_bilirubin,
            "direct_bilirubin": self.direct_bilirubin,
            "alkaline_phosphatase": self.alkaline_phosphatase,
            "sgpt_alamine_aminotransferase": self.sgpt_alamine_aminotransferase,
            "sgot_aspartate_aminotransferase": self.sgot_aspartate_aminotransferase,
            "total_protein": self.total_protein,
            "albumin": self.albumin,
            "ag_ratio": self.ag_ratio,
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient_id:
             data.update(self.patient_id._get_common_features())
        return data

class HeartAssessment(db.Document):
    meta = {'collection': 'heart_assessments'}
    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    assessed_by_admin_id = me.ReferenceField('User', reverse_delete_rule=me.NULLIFY)
    assessed_at = me.DateTimeField(default=datetime.utcnow)
    
    diabetes = me.BooleanField(default=False)
    hypertension = me.BooleanField(default=False)
    obesity = me.BooleanField(default=False)
    smoking = me.BooleanField(default=False)
    alcohol_consumption = me.BooleanField(default=False)
    physical_activity = me.BooleanField(default=False)
    diet_score = me.IntField()
    cholesterol_level = me.FloatField(required=True)
    triglyceride_level = me.FloatField()
    ldl_level = me.FloatField()
    hdl_level = me.FloatField()
    systolic_bp = me.IntField(required=True)
    diastolic_bp = me.IntField(required=True)
    air_pollution_exposure = me.FloatField()
    family_history = me.BooleanField(default=False)
    stress_level = me.IntField()
    heart_attack_history = me.BooleanField(default=False)

    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "diabetes": self.diabetes,
            "hypertension": self.hypertension,
            "obesity": self.obesity,
            "smoking": self.smoking,
            "alcohol_consumption": self.alcohol_consumption,
            "physical_activity": self.physical_activity,
            "diet_score": self.diet_score,
            "cholesterol_level": self.cholesterol_level,
            "triglyceride_level": self.triglyceride_level,
            "ldl_level": self.ldl_level,
            "hdl_level": self.hdl_level,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "air_pollution_exposure": self.air_pollution_exposure,
            "family_history": self.family_history,
            "stress_level": self.stress_level,
            "heart_attack_history": self.heart_attack_history,
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient_id:
             data.update(self.patient_id._get_common_features())
        return data

class MentalHealthAssessment(db.Document):
    meta = {'collection': 'mental_health_assessments'}
    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    assessed_by_admin_id = me.ReferenceField('User', reverse_delete_rule=me.NULLIFY)
    assessed_at = me.DateTimeField(default=datetime.utcnow)
    
    phq_score = me.IntField(required=True)
    gad_score = me.IntField(required=True)
    depressiveness = me.BooleanField(default=False)
    suicidal = me.BooleanField(default=False)
    anxiousness = me.BooleanField(default=False)
    sleepiness = me.BooleanField(default=False)

    def to_dict(self, include_patient_data=False):
        data = {
            "assessment_id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "phq_score": self.phq_score,
            "gad_score": self.gad_score,
            "depressiveness": self.depressiveness,
            "suicidal": self.suicidal,
            "anxiousness": self.anxiousness,
            "sleepiness": self.sleepiness,
            "assessed_at": self.assessed_at.isoformat()
        }
        if include_patient_data and self.patient_id:
             data.update(self.patient_id._get_common_features())
        return data

class RiskPrediction(db.Document):
    meta = {'collection': 'risk_predictions'}
    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    
    diabetes_risk_score = me.FloatField()
    diabetes_risk_level = me.StringField(max_length=20)
    liver_risk_score = me.FloatField()
    liver_risk_level = me.StringField(max_length=20)
    heart_risk_score = me.FloatField()
    heart_risk_level = me.StringField(max_length=20)
    mental_health_risk_score = me.FloatField()
    mental_health_risk_level = me.StringField(max_length=20)
    
    model_version = me.StringField(max_length=50, default='1.0')
    predicted_at = me.DateTimeField(default=datetime.utcnow)

    def _get_level(self, score):
        thresholds = current_app.config.get('RISK_THRESHOLDS', {'medium': 0.35, 'high': 0.7})
        if score >= thresholds['high']:
            return 'High'
        if score >= thresholds['medium']:
            return 'Medium'
        return 'Low'

    def update_risk(self, model_key: str, score: float, model_version: str):
        level = self._get_level(score)
        setattr(self, f"{model_key}_risk_score", score)
        setattr(self, f"{model_key}_risk_level", level)
        self.model_version = model_version

    def to_dict(self):
        return {
            "prediction_id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "diabetes_risk_score": self.diabetes_risk_score,
            "diabetes_risk_level": self.diabetes_risk_level,
            "liver_risk_score": self.liver_risk_score,
            "liver_risk_level": self.liver_risk_level,
            "heart_risk_score": self.heart_risk_score,
            "heart_risk_level": self.heart_risk_level,
            "mental_health_risk_score": self.mental_health_risk_score,
            "mental_health_risk_level": self.mental_health_risk_level,
            "model_version": self.model_version,
            "predicted_at": self.predicted_at.isoformat()
        }

class LifestyleRecommendation(db.Document):
    meta = {'collection': 'lifestyle_recommendations'}
    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    disease_type = me.StringField(max_length=50, required=True)
    risk_level = me.StringField(max_length=20, required=True)
    category = me.StringField(max_length=50, required=True)
    recommendation_text = me.StringField(required=True)
    priority = me.IntField()
    created_at = me.DateTimeField(default=datetime.utcnow)
    is_active = me.BooleanField(default=True)

    def to_dict(self):
        return {
            "recommendation_id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "disease_type": self.disease_type,
            "risk_level": self.risk_level,
            "category": self.category,
            "recommendation_text": self.recommendation_text,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }

class Consultation(db.Document):
    meta = {'collection': 'consultations'}
    
    STATUS_BOOKED = 'Booked'
    STATUS_REQUESTED = 'Requested'
    STATUS_CONFIRMED = 'Confirmed'
    STATUS_CANCELLED = 'Cancelled'
    STATUS_COMPLETED = 'Completed'

    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    admin_id = me.ReferenceField('User', reverse_delete_rule=me.NULLIFY)
    
    disease = me.StringField(max_length=50)
    consultation_type = me.StringField(max_length=50, required=True)
    consultation_datetime = me.DateTimeField(required=True)
    notes = me.StringField()
    status = me.StringField(max_length=20, default='Booked')
    created_at = me.DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "patient_name": self.patient_id.name if self.patient_id else "Unknown",
            "admin_id": str(self.admin_id.pk) if self.admin_id else None,
            "doctor_name": self.admin_id.name if self.admin_id else "System/Pending",
            "disease": self.disease,
            "consultation_type": self.consultation_type,
            "consultation_datetime": self.consultation_datetime.isoformat() if self.consultation_datetime else None,
            "notes": self.notes,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "patient_risk_info": RiskPrediction.objects(patient_id=self.patient_id).first().to_dict() if self.patient_id and RiskPrediction.objects(patient_id=self.patient_id).first() else None
        }

class ConsultationNote(db.Document):
    meta = {'collection': 'consultation_notes'}
    patient_id = me.ReferenceField('Patient', reverse_delete_rule=me.CASCADE, required=True)
    admin_id = me.ReferenceField('User', reverse_delete_rule=me.NULLIFY)
    notes = me.StringField(required=True)
    created_at = me.DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "note_id": str(self.id),
            "patient_id": str(self.patient_id.pk),
            "admin_id": str(self.admin_id.pk) if self.admin_id else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }

class TokenBlocklist(db.Document):
    meta = {'collection': 'token_blocklist'}
    jti = me.StringField(max_length=36, required=True, unique=True)
    token_type = me.StringField(max_length=10, required=True)
    user_id = me.StringField() # Storing as string representation of ID
    created_at = me.DateTimeField(default=datetime.utcnow)
    expires_at = me.DateTimeField()
