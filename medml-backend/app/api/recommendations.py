# HealthCare App/medml-backend/app/api/recommendations.py
from flask import jsonify, current_app, request
from . import api_bp
from app.models import db, Patient
from app.api.decorators import admin_required
from flask_jwt_extended import jwt_required
from app.services import get_gemini_recommendations
from .responses import ok, forbidden, server_error

@api_bp.route('/patients/<patient_id>/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations(patient_id):
    """
    [Admin/Patient] Fetches lifestyle recommendations based on *latest* risk.
    Patient can only access their own.
    """
    try:
        # 1. Check permissions
        from .decorators import parse_jwt_identity
        jwt_identity = parse_jwt_identity()
        user_role = jwt_identity.get('role')
        user_id = jwt_identity.get('id')
        
        if user_role == 'patient' and user_id != patient_id:
            return forbidden("Patients can only access their own report")
        
        patient = Patient.objects(id=patient_id).first()
        if not patient:
            return not_found("Patient not found")

        # --- UPDATED: Get latest prediction from 1:N ---
        risk_prediction = RiskPrediction.objects(patient_id=patient).order_by('-predicted_at').first()
        
        if not risk_prediction:
            # No predictions yet, return empty
            return ok({"diet": [], "exercise": [], "sleep": [], "lifestyle": []})

        risk_map = {
            'diabetes': risk_prediction.diabetes_risk_level,
            'liver': risk_prediction.liver_risk_level,
            'heart': risk_prediction.heart_risk_level,
            'mental_health': risk_prediction.mental_health_risk_level
        }
        
        # Call Gemini Service
        recommendations_data = get_gemini_recommendations(risk_map)
        
        # Return the grouped-by-category dictionary
        return ok(recommendations_data)

    except Exception as e:
        current_app.logger.error(f"Error fetching recommendations: {e}")
        return server_error(str(e))