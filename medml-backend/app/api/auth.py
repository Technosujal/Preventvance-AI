# HealthCare App/medml-backend/app/api/auth.py
from flask import request, jsonify, abort, current_app
from . import api_bp
from app.models import User, Patient, TokenBlocklist
from app.extensions import db, limiter
from app.schemas import UserRegisterSchema, UserLoginSchema, PatientLoginSchema, PatientCreateSchema, PASSWORD_ERROR_MSG
from pydantic import ValidationError
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    get_jti
)
from .decorators import parse_jwt_identity
from datetime import datetime # Added
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

# Rate limiting to login endpoints
LOGIN_LIMIT = "10 per minute"

@api_bp.route('/auth/admin/register', methods=['POST'])
@limiter.limit("5 per hour") # Stricter limit for registration
def register_admin():
    """
    Registers a new Admin (Healthcare Worker).
    """
    try:
        data = UserRegisterSchema(**request.json)
    except ValidationError as e:
        if any('regex' in err['type'] for err in e.errors()):
            return unprocessable_entity(message=PASSWORD_ERROR_MSG)
        return unprocessable_entity(messages=e.errors())

    if User.objects(email=data.email).first():
        return conflict("Email already exists")
    
    if data.username and User.objects(username=data.username).first():
        return conflict("Username already exists")

    new_user = User(
        name=data.name,
        email=data.email,
        username=data.username,
        designation=data.designation,
        contact_number=data.contact_number,
        facility_name=data.facility_name,
        role='admin' # Enforce admin role
    )
    new_user.set_password(data.password)
    
    try:
        new_user.save()
    except Exception as e:
        current_app.logger.error(f"Error registering admin: {e}")
        return server_error("Could not register admin.")

    current_app.logger.info(f"New admin registered: {new_user.email}")
    return created({"message": "Admin registered successfully", "user": new_user.to_dict()})

@api_bp.route('/auth/admin/login', methods=['POST'])
@limiter.limit(LOGIN_LIMIT) # Apply rate limit
def login_admin():
    """
    Logs in an Admin (Healthcare Worker) using username or email.
    """
    try:
        data = request.json
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username_or_email or not password:
            return unprocessable_entity(message="Username/email and password are required")
    except Exception:
        return unprocessable_entity(message="Invalid request format")

    # Try to find user by username first, then by email
    user = User.objects(username=username_or_email).first()
    if not user:
        user = User.objects(email=username_or_email).first()

    if user and user.check_password(password):
        # Create token with role identity string formatting
        identity = f"{user.id}:{user.role}:{user.name}"
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        current_app.logger.info(f"Admin login successful: {user.username or user.email}")
        return ok({
            "message": "Admin login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "admin_id": str(user.id),
            "name": user.name,
        })
    
    current_app.logger.warning(f"Failed admin login attempt for: {username_or_email[:3]}***")
    return unauthorized("Invalid username/email or password.")

@api_bp.route('/auth/patient/register', methods=['POST'])
@limiter.limit("5 per hour") # Stricter limit for registration
def register_patient():
    """
    Registers a new Patient.
    """
    try:
        data = PatientCreateSchema(**request.json)
    except ValidationError as e:
        if any('regex' in err['type'] for err in e.errors()):
            return unprocessable_entity(message=PASSWORD_ERROR_MSG)
        return unprocessable_entity(messages=e.errors())

    try:
        new_patient.save()
    except Exception as e:
        current_app.logger.error(f"Error registering patient: {e}")
        return server_error("Could not register patient.")

    current_app.logger.info(f"New patient registered: {new_patient.abha_id}")
    return created({"message": "Patient registered successfully", "patient": new_patient.to_dict()})

@api_bp.route('/auth/patient/login', methods=['POST'])
@limiter.limit(LOGIN_LIMIT) # Apply rate limit
def login_patient():
    """
    Logs in a Patient using ABHA ID and password.
    """
    try:
        data = PatientLoginSchema(**request.json)
    except ValidationError as e:
        return unprocessable_entity(messages=e.errors())

    patient = Patient.objects(abha_id=data.abha_id).first()

    if patient and patient.check_password(data.password):
        # Create token with role identity string formatting
        identity = f"{patient.id}:patient:{patient.name}"
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        current_app.logger.info(f"Patient login successful: {patient.abha_id}")
        return ok({
            "message": "Patient login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "patient_id": str(patient.id),
            "name": patient.name,
        })
    
    current_app.logger.warning(f"Failed patient login attempt for ABHA ID: {data.abha_id}")
    return unauthorized("Invalid ABHA ID or password.")


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refreshes an access token.
    """
    try:
        identity = parse_jwt_identity()
        current_jti = get_jwt().get('jti')
        
        # Blocklist the used refresh token
        TokenBlocklist(jti=current_jti, token_type='refresh', user_id=identity.get('id')).save()

        # Create new tokens
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        return ok({"access_token": access_token, "refresh_token": refresh_token})
    except Exception as e:
        current_app.logger.error(f"Error refreshing token: {e}")
        return unauthorized("Token refresh failed")


@api_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logs out a user by blocklisting their token.
    """
    jwt_payload = get_jwt()
    jti = jwt_payload.get("jti")
    token_type = jwt_payload.get("type", "access")
    expires = datetime.fromtimestamp(jwt_payload.get("exp"))
    identity = parse_jwt_identity() or {}
    try:
        TokenBlocklist(jti=jti, token_type=token_type, user_id=identity.get('id'), expires_at=expires).save()
    except Exception as e:
        current_app.logger.error(f"Failed to revoke token: {e}")
        return server_error("Failed to revoke token")
    return ok({"message": "Token successfully revoked"})


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Returns the profile of the currently authenticated user (Admin or Patient).
    """
    try:
        jwt_identity = parse_jwt_identity()
        user_id = jwt_identity.get('id')
        user_role = jwt_identity.get('role')

        if not user_id or not user_role:
            return unauthorized("Invalid token identity")

        if user_role == 'admin':
            user = User.objects(id=user_id).first()
            if not user:
                return not_found("User not found")
            return ok(user.to_dict())
        elif user_role == 'patient':
            patient = Patient.objects(id=user_id).first()
            if not patient:
                return not_found("Patient not found")
            # Patient dashboard needs history and latest prediction
            return ok(patient.to_dict(
                include_admin=True,
                include_history=True, 
                include_latest_prediction=True,
                include_notes=True
            ))
        
        return unauthorized("Unknown user role")
        
    except Exception as e:
        current_app.logger.error(f"Error in /me endpoint: {e}")
        return server_error()

@api_bp.route('/admins', methods=['GET'])
@jwt_required()
def get_all_admins():
    """
    Returns a list of all registered healthcare workers (admins).
    """
    admins = User.objects(role='admin')
    return ok({"admins": [a.to_dict() for a in admins]})