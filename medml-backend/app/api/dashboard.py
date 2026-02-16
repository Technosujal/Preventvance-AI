# HealthCare App/medml-backend/app/api/dashboard.py
from flask import jsonify, current_app
from . import api_bp
from app.models import Patient, RiskPrediction
from app.extensions import db
from app.extensions import limiter
from app.api.decorators import admin_required
from flask_jwt_extended import jwt_required
from datetime import date, datetime, timedelta
from .responses import ok, server_error

@api_bp.route('/dashboard/stats', methods=['GET']) # Renamed route
@jwt_required()
@admin_required
@limiter.limit("100 per minute")  # More permissive limit for dashboard stats
def get_dashboard_stats(): # Renamed function
    """
    [Admin Only] Provides analytics for the admin dashboard.
    Returns counts as per frontend api_client.
    """
    try:
        # 1. Today's Registrations
        today = date.today()
        tomorrow = today + timedelta(days=1)
        # Convert date to datetime for range query
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(tomorrow, datetime.min.time())

        todays_registrations_count = Patient.objects(created_at__gte=start_of_day, created_at__lt=end_of_day).count()

        # 2. Count by disease risk (Medium OR High)
        # Using objects().filter() for clarity
        diabetes_risk_count = RiskPrediction.objects(diabetes_risk_level__in=['Medium', 'High']).count()
        liver_risk_count = RiskPrediction.objects(liver_risk_level__in=['Medium', 'High']).count()
        heart_risk_count = RiskPrediction.objects(heart_risk_level__in=['Medium', 'High']).count()
        mental_health_risk_count = RiskPrediction.objects(mental_health_risk_level__in=['Medium', 'High']).count()
        
        # Total registered patients
        total_patients_count = Patient.objects().count()
        
        # Additional stats
        week_ago = start_of_day - timedelta(days=7)
        this_week_registrations = Patient.objects(created_at__gte=week_ago).count()
        
        month_start = datetime.combine(today.replace(day=1), datetime.min.time())
        this_month_registrations = Patient.objects(created_at__gte=month_start).count()
        
        # Total assessments count
        total_assessments = RiskPrediction.objects().count()

        # --- UPDATED: Enhanced response with more analytics ---
        stats_data = {
            "today_registrations": todays_registrations_count,
            "this_week_registrations": this_week_registrations,
            "this_month_registrations": this_month_registrations,
            "total_patients": total_patients_count,
            "total_assessments": total_assessments,
            "diabetes_risk_count": diabetes_risk_count,
            "liver_risk_count": liver_risk_count,
            "heart_risk_count": heart_risk_count,
            "mental_health_risk_count": mental_health_risk_count
        }
        
        return ok(stats_data) # Return flat JSON

    except Exception as e:
        current_app.logger.error(f"Error fetching dashboard stats: {e}")
        return server_error()