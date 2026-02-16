# HealthCare App/medml-backend/app/api/chat.py
from flask import request, jsonify
from . import api_bp
from app.services import get_chatbot_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from .responses import ok, bad_request, server_error

@api_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """
    AI Chatbot endpoint for medical assistance.
    """
    data = request.json
    message = data.get('message')
    history = data.get('history', []) # List of {role: 'user'|'model', content: '...'}

    if not message:
        return bad_request("Message is required")

    try:
        response_text = get_chatbot_response(message, history)
        return ok({"response": response_text})
    except Exception as e:
        return server_error(f"Chat error: {str(e)}")
