# HealthCare App/medml-backend/app/api/consultations.py
from flask import request, jsonify, current_app
from . import api_bp
from app.models import Patient, Consultation, ConsultationNote, User, DoctorAvailability
from app.extensions import db
from app.api.decorators import admin_required, patient_required, get_current_admin_id, get_current_user_id, parse_jwt_identity
from pydantic import BaseModel, constr, ValidationError
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from .responses import created, bad_request, not_found, server_error, ok, forbidden, conflict

# --- UPDATED: Schema removed, using direct JSON ---

@api_bp.route('/consultations/available-slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    """
    Calculates free time slots for a doctor on a specific date.
    """
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date') # YYYY-MM-DD

    if not doctor_id or not date_str:
        return bad_request("Missing doctor_id or date")

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return bad_request("Invalid date format. Use YYYY-MM-DD")

    # 1. Get doctor's availability for that day of week
    day_of_week = target_date.weekday()
    availability = DoctorAvailability.objects(doctor_id=doctor_id, day_of_week=day_of_week).first()

    if not availability:
        return ok({"slots": [], "message": "Doctor has no availability set for this day."})

    # 2. Generate all possible slots
    start_time = datetime.strptime(availability.start_time, "%H:%M").time()
    end_time = datetime.strptime(availability.end_time, "%H:%M").time()
    duration = availability.slot_duration

    all_slots = []
    current_dt = datetime.combine(target_date, start_time)
    end_dt = datetime.combine(target_date, end_time)

    while current_dt + timedelta(minutes=duration) <= end_dt:
        all_slots.append(current_dt)
        current_dt += timedelta(minutes=duration)

    # 3. Get existing bookings for that doctor and date
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    existing_bookings = Consultation.objects(
        admin_id=doctor_id,
        consultation_datetime__gte=start_of_day,
        consultation_datetime__lte=end_of_day,
        status__ne=Consultation.STATUS_CANCELLED
    )

    booked_times = [b.consultation_datetime for b in existing_bookings]

    # 4. Filter out booked slots
    # Note: Using simple exact match for now. In production, consider overlaps.
    available_slots = [
        slot.strftime("%H:%M") for slot in all_slots 
        if slot not in booked_times
    ]

    return ok({"slots": available_slots})

@api_bp.route('/consultations/availability', methods=['GET'])
@jwt_required()
@admin_required
def get_my_availability():
    """
    [Admin/Doctor Only] Gets the logged-in doctor's availability rules.
    """
    admin_id = get_current_admin_id()
    availabilities = DoctorAvailability.objects(doctor_id=admin_id)
    return ok({"availabilities": [a.to_dict() for a in availabilities]})

@api_bp.route('/consultations/availability', methods=['POST'])
@jwt_required()
@admin_required
def update_availability():
    """
    [Admin/Doctor Only] Bulk updates doctor's availability.
    Expects a list of {day_of_week, start_time, end_time, slot_duration}
    """
    admin_id = get_current_admin_id()
    data = request.json # List of availability objects

    if not isinstance(data, list):
        return bad_request("Expected a list of availability rules")

    try:
        # Clear existing
        DoctorAvailability.objects(doctor_id=admin_id).delete()

        for item in data:
            new_avail = DoctorAvailability(
                doctor_id=admin_id,
                day_of_week=item.get('day_of_week'),
                start_time=item.get('start_time'),
                end_time=item.get('end_time'),
                slot_duration=item.get('slot_duration', 30)
            )
            new_avail.save()
        
        return ok({"message": "Availability updated successfully"})
    except Exception as e:
        current_app.logger.error(f"Error updating availability: {e}")
        return server_error("Could not update availability.")

# Update existing book_consultation to handle better association
@api_bp.route('/consultations', methods=['POST'])
@jwt_required()
def book_consultation():
    """
    Books a consultation.
    - Admin can book for any patient.
    - Patient can book for themselves.
    """
    data = request.json
    identity = parse_jwt_identity()
    user_id = identity.get('id')
    user_role = identity.get('role')

    patient_id = data.get('patient_id')
    if user_role == 'patient':
        patient_id = user_id # Enforce self-booking
    
    doctor_id = data.get('doctor_id') or data.get('admin_id')
    disease = data.get('disease')
    consultation_type = data.get('consultation_type', 'teleconsultation')
    consultation_datetime_str = data.get('consultation_datetime')

    if not all([patient_id, doctor_id, disease, consultation_datetime_str]):
        return bad_request("Missing required fields")

    try:
        consultation_datetime = datetime.fromisoformat(consultation_datetime_str.replace('Z', '+00:00'))
    except ValueError:
        return bad_request("Invalid datetime format")

    # Check if slot is already booked (double book prevention)
    exists = Consultation.objects(
        admin_id=doctor_id,
        consultation_datetime=consultation_datetime,
        status__ne=Consultation.STATUS_CANCELLED
    ).first()
 
    if exists:
        return conflict("This time slot is already booked.")

    new_consultation = Consultation(
        patient_id=patient_id,
        admin_id=doctor_id,
        disease=disease,
        consultation_type=consultation_type,
        consultation_datetime=consultation_datetime,
        notes=data.get('notes', f"Booking for {disease}"),
        status=Consultation.STATUS_CONFIRMED if user_role == 'admin' else Consultation.STATUS_REQUESTED
    )
    
    try:
        new_consultation.save()
        return created({
            "message": "Consultation booked successfully",
            "consultation": new_consultation.to_dict(),
        })
    except Exception as e:
        current_app.logger.error(f"Error booking consultation: {e}")
        return server_error("Could not book consultation.")

@api_bp.route('/consultations', methods=['GET'])
@jwt_required()
def get_all_consultations():
    """
    Gets consultations. 
    - Admin sees all.
    - Patient sees only theirs.
    """
    identity = parse_jwt_identity()
    user_id = identity.get('id')
    user_role = identity.get('role')

    if user_role == 'admin':
        consultations = Consultation.objects().order_by('-created_at')
    else:
        consultations = Consultation.objects(patient_id=user_id).order_by('-created_at')
    
    return ok({"consultations": [c.to_dict() for c in consultations]})

# Re-implementing other necessary routes if needed, but keeping it concise
@api_bp.route('/consultations/<consultation_id>', methods=['PATCH'])
@jwt_required()
def update_consultation():
    """
    Updates consultation. 
    - Admin can update any consultation.
    - Patient can update their own requested/confirmed appointments (e.g. reschedule).
    """
    from app.api.decorators import parse_jwt_identity # Local import to avoid circular dep if any
    identity = parse_jwt_identity()
    user_id = identity.get('id')
    user_role = identity.get('role')

    consultation = Consultation.objects(id=consultation_id).first()
    if not consultation:
        return not_found("Consultation not found")
    
    # Authorization check
    if user_role == 'patient' and consultation.patient_id != user_id:
        return forbidden("You can only update your own consultations")

    data = request.json

    if 'status' in data:
        # Patients can only cancel their own
        if user_role == 'patient' and data['status'] not in [Consultation.STATUS_CANCELLED]:
             return forbidden("Patients can only change status to Cancelled")
        consultation.status = data['status']
        
    if 'consultation_datetime' in data:
        try:
            consultation.consultation_datetime = datetime.fromisoformat(data['consultation_datetime'].replace('Z', '+00:00'))
            # If a patient reschedules, we might want to reset status to Requested if it was Confirmed
            if user_role == 'patient' and consultation.status == Consultation.STATUS_CONFIRMED:
                consultation.status = Consultation.STATUS_REQUESTED
        except ValueError:
            return bad_request("Invalid datetime format")
            
    if 'admin_id' in data and user_role == 'admin':
        consultation.admin_id = data['admin_id']
    if 'notes' in data:
        consultation.notes = data['notes']

    try:
        consultation.save()
        return ok({
            "message": "Consultation updated successfully",
            "consultation": consultation.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error updating consultation: {e}")
        return server_error("Could not update consultation.")

@api_bp.route('/consultations/<consultation_id>', methods=['DELETE'])
@jwt_required()
def delete_consultation(consultation_id):
    """
    Cancels/Deletes a consultation.
    """
    identity = parse_jwt_identity()
    user_id = identity.get('id')
    user_role = identity.get('role')

    consultation = Consultation.objects(id=consultation_id).first()
    if not consultation:
        return not_found("Consultation not found")
    
    if user_role == 'patient' and consultation.patient_id != user_id:
        return forbidden("You can only cancel your own consultations")

    try:
        # Instead of hard delete, usually we just set status to Cancelled.
        consultation.status = Consultation.STATUS_CANCELLED
        consultation.save()
        return ok({"message": "Consultation cancelled successfully"})
    except Exception as e:
        current_app.logger.error(f"Error cancelling consultation: {e}")
        return server_error("Could not cancel consultation.")

@api_bp.route('/consultations/notes', methods=['POST'])
@jwt_required()
@admin_required
def add_consultation_note():
    data = request.json
    patient_id = data.get('patient_id')
    notes = data.get('notes')
    
    if not patient_id or not notes:
        return bad_request("Missing patient_id or notes")
        
    new_note = ConsultationNote(
        patient_id=patient_id,
        admin_id=get_current_admin_id(),
        notes=notes
    )
    
    try:
        new_note.save()
        return created({"message": "Note added successfully", "note": new_note.to_dict()})
    except Exception as e:
        current_app.logger.error(f"Error adding consultation note: {e}")
        return server_error("Internal error")