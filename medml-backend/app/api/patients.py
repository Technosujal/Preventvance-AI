# HealthCare App/medml-backend/app/api/patients.py
from flask import request, jsonify, current_app
from . import api_bp
from app.models import Patient, User, RiskPrediction
from app.extensions import limiter, db
from app.schemas import PatientCreateSchema, PatientUpdateSchema
from app.api.decorators import admin_required, get_current_admin_id, parse_jwt_identity
from pydantic import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
# Removed SQLAlchemy imports
from .responses import (
    ok,
    created,
    bad_request,
    unauthorized,
    forbidden,
    not_found,
    conflict,
    unprocessable_entity,
    server_error,
)

@api_bp.route('/patients', methods=['POST'])
@jwt_required()
@admin_required
def create_patient():
    """
    [Admin Only] Creates a new patient record.
    """
    try:
        current_app.logger.info(f"Received patient data: {request.json}")
        data = PatientCreateSchema(**request.json)
        current_app.logger.info(f"Validated patient data: {data}")
    except ValidationError as e:
        current_app.logger.error(f"Validation error: {e.errors()}")
        return unprocessable_entity(messages=e.errors())
    
    admin_id = get_current_admin_id()
    if not admin_id:
        return unauthorized("Admin ID not found")
    
    if Patient.objects(abha_id=data.abha_id).first():
        return conflict("Patient with this ABHA ID already exists")

    new_patient = Patient(
        name=data.name, # Updated from full_name
        age=data.age,
        gender=data.gender,
        height=data.height, # Updated from height_cm
        weight=data.weight, # Updated from weight_kg
        abha_id=data.abha_id,
        state_name=data.state_name,
        created_by_admin_id=admin_id # Updated from created_by_user_id
    )
    new_patient.set_password(data.password) 

    try:
        new_patient.save()
        current_app.logger.info(f"Admin {admin_id} created patient {new_patient.id} with ABHA ID {new_patient.abha_id}")
        
        return created({
            "message": "Patient created successfully",
            "patient": new_patient.to_dict(),
            "patient_id": str(new_patient.id),
            "name": new_patient.name,
        })
    
    except Exception as e:
        current_app.logger.error(f"Error creating patient: {e}")
        return server_error("An unexpected error occurred.")

@api_bp.route('/patients', methods=['GET'])
@jwt_required()
@admin_required
@limiter.limit("100 per minute")  # More permissive limit for patient listing
def get_patients():
    """
    [Admin Only] Gets a list of all patients, with filtering and sorting
    matching the frontend api_client.
    """
    try:
        # Simplified listing for MongoDB
        disease = request.args.get('disease')
        sort = request.args.get('sort', 'recently_added')
        
        # Use aggregation or separate queries for risk filtering
        # For now, let's just get all and filter in memory if needed, or implement basic sorting
        # Re-implementing more efficiently for MongoDB
        if disease or sort != 'recently_added':
            # This logic needs careful translation. For now, we'll fetch patients and their latest predictions.
            # In a real Mongo app, we might store the latest risk level on the Patient document.
            all_patients = Patient.objects().order_by('-created_at')
            # Filtering in memory for simplicity in this migration step
            # A more robust version would use MongoDB aggregations
            results = []
            for p in all_patients:
                p_dict = p.to_dict(include_latest_prediction=True)
                latest = p_dict.get('latest_prediction')
                
                match = True
                if disease:
                    if not latest:
                        match = False
                    else:
                        level = latest.get(f'{disease}_risk_level')
                        if sort == 'high_risk' and level != 'High': match = False
                        elif sort == 'medium_risk' and level != 'Medium': match = False
                        elif sort == 'low_risk' and level != 'Low': match = False
                elif sort == 'high_risk':
                    if not latest or not any(v == 'High' for k, v in latest.items() if '_risk_level' in k):
                        match = False
                elif sort == 'medium_risk':
                    if not latest or not any(v == 'Medium' for k, v in latest.items() if '_risk_level' in k):
                        match = False
                
                if match:
                    results.append(p_dict)
            return ok(results)
        
        patients = Patient.objects().order_by('-created_at')
        patients_data = [p.to_dict(include_latest_prediction=True) for p in patients]
        
        # Return list, including latest prediction data for the dashboard view
        patients_data = [p.to_dict(include_latest_prediction=True) for p in patients]
        
        return ok(patients_data)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching patients: {e}")
        return server_error(str(e))


@api_bp.route('/patients/<patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    """
    [Admin/Patient] Gets detailed info for a single patient.
    Patient can only access their own.
    """
    # Check permissions
    jwt_identity = parse_jwt_identity()
    user_role = jwt_identity.get('role')
    user_id = jwt_identity.get('id')
    
    if user_role == 'patient' and user_id != patient_id:
        return forbidden("Patients can only access their own data")

    patient = Patient.objects(id=patient_id).first()
    if not patient:
        return not_found("Patient not found")
    
    # Return full details including all history and notes for Admin view
    return ok(patient.to_dict(
        include_admin=True,
        include_history=True, 
        include_latest_prediction=True,
        include_notes=True
    ))


@api_bp.route('/patients/<patient_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_patient(patient_id):
    """
    [Admin Only] Updates a patient's basic info.
    """
    patient = Patient.objects(id=patient_id).first()
    if not patient:
        return not_found("Patient not found")
    
    try:
        data = PatientUpdateSchema(**request.json)
    except ValidationError as e:
        return unprocessable_entity(messages=e.errors())

    # Check for ABHA ID conflict if it's being changed
    if data.abha_id != patient.abha_id:
        if Patient.objects(abha_id=data.abha_id, id__ne=patient_id).first():
            return conflict("Patient with this ABHA ID already exists")
    
    try:
        # Update mutable fields
        patient.name = data.name
        patient.age = data.age
        patient.gender = data.gender
        patient.state_name = data.state_name
        patient.height = data.height
        patient.weight = data.weight
        patient.abha_id = data.abha_id # Allow ABHA ID update

        patient.save()
        current_app.logger.info(f"Patient {patient_id} updated by admin {get_current_admin_id()}")
        
        return ok({"message": "Patient updated successfully", "patient": patient.to_dict()})

    except Exception as e:
        current_app.logger.error(f"Error updating patient {patient_id}: {e}")
        return server_error()