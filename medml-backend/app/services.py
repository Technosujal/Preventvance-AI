# HealthCare App/medml-backend/app/services.py
import joblib
import pandas as pd
import numpy as np
import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from flask import current_app

# Path to models_store directory
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models_store')

# Global dictionary to hold models and preprocessors
models = {
    'diabetes': None,
    'heart': None,
    'liver': None,
    'mental_health': None
}

def load_model(app: Any, key: str, filename: str):
    """Loads a .pkl model from the models_store directory into a global dict."""
    try:
        path = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(path):
            app.logger.warning(f"Model file not found at {path}. Predictions for '{key}' will fail.")
            return None
        return joblib.load(path)
    except Exception as e:
        app.logger.error(f"Error loading model {filename}: {e}")
        return None

def load_models(app: Any):
    """Loads all models and preprocessors at application startup."""
    with app.app_context():
        app.logger.info(f"Loading models from: {MODEL_DIR}")
        
        models['diabetes'] = load_model(app, 'diabetes', 'diabetes_LightGBM SMOTE.pkl')
        models['heart'] = load_model(app, 'heart', 'heart_SVM Weighted Tuned.pkl')
        models['liver'] = load_model(app, 'liver', 'liver_LightGBM SMOTE.pkl')
        # Use depressiveness model as the main mental health model
        models['mental_health'] = load_model(app, 'mental_health', 'mental_health_depressiveness_Logistic Regression.pkl')
        
        app.logger.info("Model loading complete.")
        
        # --- Configure Gemini ---
        try:
            api_key = app.config.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                app.logger.info("Gemini API configured successfully.")
            else:
                app.logger.warning("GEMINI_API_KEY is not set. Recommendation service will be disabled.")
        except Exception as e:
            app.logger.error(f"Error configuring Gemini API: {e}")

# --- Preprocessing & Prediction Logic ---

def predict_diabetes(data: Dict[str, Any]) -> float:
    model = models.get('diabetes')
    if model is None:
        current_app.logger.error("Diabetes model is not loaded.")
        raise RuntimeError("Diabetes model is not loaded.")
        
    try:
        processed_data = {}
        processed_data['Pregnancies'] = 1 if data.get('pregnancy') else 0
        processed_data['Glucose'] = data.get('glucose', 0)
        processed_data['BloodPressure'] = data.get('blood_pressure', 0)
        processed_data['SkinThickness'] = data.get('skin_thickness', 0)
        processed_data['Insulin'] = data.get('insulin', 0)
        processed_data['BMI'] = data.get('bmi', 0)
        processed_data['Age'] = data.get('age', 0)
        
        glucose = processed_data['Glucose']
        age = processed_data['Age']
        bmi = processed_data['BMI']
        
        processed_data['DiabetesPedigreeFunction'] = (glucose * age * bmi) / 10000.0 if glucose and age and bmi else 0.5
        
        if age < 30:
            processed_data['AgeGroup'] = 0
        elif age < 50:
            processed_data['AgeGroup'] = 1
        else:
            processed_data['AgeGroup'] = 2
            
        if bmi < 18.5:
            processed_data['BMICategory'] = 0
        elif bmi < 25:
            processed_data['BMICategory'] = 1
        elif bmi < 30:
            processed_data['BMICategory'] = 2
        else:
            processed_data['BMICategory'] = 3
            
        if glucose < 100:
            processed_data['GlucoseCategory'] = 0
        elif glucose < 126:
            processed_data['GlucoseCategory'] = 1
        else:
            processed_data['GlucoseCategory'] = 2
            
        processed_data['BMIAgeInteraction'] = bmi * age
        processed_data['GlucoseBMIInteraction'] = glucose * bmi
        
        feature_order = [
            'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 
            'AgeGroup', 'BMICategory', 'GlucoseCategory', 
            'BMIAgeInteraction', 'GlucoseBMIInteraction'
        ]
        
        df = pd.DataFrame([processed_data], columns=feature_order)
        probability = model.predict_proba(df)[0][1] 
        return float(probability)
    except Exception as e:
        current_app.logger.error(f"Diabetes prediction error: {e}")
        raise ValueError("Failed to preprocess diabetes data.")

def predict_heart(data: Dict[str, Any]) -> float:
    model = models.get('heart')
    if model is None:
        current_app.logger.error("Heart model is not loaded.")
        raise RuntimeError("Heart model is not loaded.")
        
    try:
        gender_value = 1 if data.get('gender') == 'Male' else 0
        diabetes = 1 if data.get('diabetes') else 0
        hypertension = 1 if data.get('hypertension') else 0
        obesity = 1 if data.get('obesity') else 0
        smoking = 1 if data.get('smoking') else 0
        alcohol_consumption = 1 if data.get('alcohol_consumption') else 0
        physical_activity = 1 if data.get('physical_activity') else 0
        family_history = 1 if data.get('family_history') else 0
        heart_attack_history = 1 if data.get('heart_attack_history') else 0

        age = data.get('age', 0)
        bmi = data.get('bmi', 0)
        diet_score = data.get('diet_score', 0)
        cholesterol_level = data.get('cholesterol_level', 0)
        triglyceride_level = data.get('triglyceride_level', 0)
        ldl_level = data.get('ldl_level', 0)
        hdl_level = data.get('hdl_level', 0)
        systolic_bp = data.get('systolic_bp', 0)
        diastolic_bp = data.get('diastolic_bp', 0)
        air_pollution_exposure = data.get('air_pollution_exposure', 0)
        stress_level = data.get('stress_level', 0)
        
        cholesterol_hdl_ratio = cholesterol_level / hdl_level if hdl_level > 0 else 0
        ldl_hdl_ratio = ldl_level / hdl_level if hdl_level > 0 else 0
        triglyceride_hdl_ratio = triglyceride_level / hdl_level if hdl_level > 0 else 0
        bp_difference = systolic_bp - diastolic_bp
        age_bmi_interaction = age * bmi
        stress_diet_interaction = stress_level * diet_score
        age_gender_interaction = age * gender_value
        
        processed_data = {
            'Diabetes': diabetes, 'Hypertension': hypertension, 'Obesity': obesity, 'Smoking': smoking,
            'Alcohol_Consumption': alcohol_consumption, 'Physical_Activity': physical_activity,
            'Diet_Score': diet_score, 'Cholesterol_Level': cholesterol_level, 'Triglyceride_Level': triglyceride_level,
            'LDL_Level': ldl_level, 'HDL_Level': hdl_level, 'Systolic_BP': systolic_bp, 'Diastolic_BP': diastolic_bp,
            'Air_Pollution_Exposure': air_pollution_exposure, 'Family_History': family_history, 'Stress_Level': stress_level,
            'Heart_Attack_History': heart_attack_history, 'Age': age, 'Gender': gender_value, 'BMI': bmi,
            'Cholesterol_HDL_Ratio': cholesterol_hdl_ratio, 'LDL_HDL_Ratio': ldl_hdl_ratio,
            'Triglyceride_HDL_Ratio': triglyceride_hdl_ratio, 'BP_Difference': bp_difference,
            'Age_BMI_Interaction': age_bmi_interaction, 'Stress_Diet_Interaction': stress_diet_interaction,
            'Age_Gender_Interaction': age_gender_interaction
        }
        
        feature_columns = [
            'Diabetes', 'Hypertension', 'Obesity', 'Smoking', 'Alcohol_Consumption',
            'Physical_Activity', 'Diet_Score', 'Cholesterol_Level', 'Triglyceride_Level',
            'LDL_Level', 'HDL_Level', 'Systolic_BP', 'Diastolic_BP', 'Air_Pollution_Exposure',
            'Family_History', 'Stress_Level', 'Heart_Attack_History', 'Age', 'Gender', 'BMI',
            'Cholesterol_HDL_Ratio', 'LDL_HDL_Ratio', 'Triglyceride_HDL_Ratio', 'BP_Difference',
            'Age_BMI_Interaction', 'Stress_Diet_Interaction', 'Age_Gender_Interaction'
        ]
        
        df = pd.DataFrame([processed_data], columns=feature_columns)
        try:
            probability = model.predict_proba(df)[0][1]
            return float(probability)
        except Exception:
            risk_score = 0.0
            if diabetes or hypertension or smoking: risk_score += 0.3
            if obesity: risk_score += 0.2
            if family_history: risk_score += 0.2
            if age > 50: risk_score += 0.2
            if stress_level > 5: risk_score += 0.1
            return float(min(risk_score, 1.0))
    except Exception as e:
        current_app.logger.error(f"Heart prediction error: {e}")
        raise ValueError("Failed to preprocess heart data.")

def predict_liver(data: Dict[str, Any]) -> float:
    model = models.get('liver')
    if model is None:
        current_app.logger.error("Liver model is not loaded.")
        raise RuntimeError("Liver model is not loaded.")

    try:
        data_processed = data.copy()
        data_processed['Gender'] = 1 if data_processed.get('gender') == 'Male' else 0
        albumin = data_processed.get('albumin', 0)
        total_protein = data_processed.get('total_protein', 0)
        
        if total_protein and albumin and total_protein > albumin:
            globulin = total_protein - albumin
            data_processed['Albumin_and_Globulin_Ratio'] = round(albumin / globulin, 2)
        else:
            data_processed['Albumin_and_Globulin_Ratio'] = 0.9
        
        key_map = {
            'age': 'Age', 'gender': 'Gender', 'total_bilirubin': 'TB', 'direct_bilirubin': 'DB',
            'alkaline_phosphatase': 'Alkphos', 'sgpt_alamine_aminotransferase': 'Sgpt',
            'sgot_aspartate_aminotransferase': 'Sgot', 'total_protein': 'TP', 'albumin': 'ALB',
            'ag_ratio': 'AGRatio'
        }
        
        model_input_data = {key_map.get(k, k): v for k, v in data_processed.items()}
        if model_input_data.get('AGRatio') is None:
            model_input_data['AGRatio'] = model_input_data.get('Albumin_and_Globulin_Ratio', 0.9)
        
        age = model_input_data.get('Age', 0)
        gender = model_input_data.get('Gender', 0)
        tb = model_input_data.get('TB', 0)
        db = model_input_data.get('DB', 0)
        sgpt = model_input_data.get('Sgpt', 0)
        sgot = model_input_data.get('Sgot', 0)
        tp = model_input_data.get('TP', 0)
        alb = model_input_data.get('ALB', 0)
        
        model_input_data['BilirubinRatio'] = db / tb if tb > 0 else 0
        model_input_data['SGPTSGOTRatio'] = sgpt / sgot if sgot > 0 else 0
        model_input_data['TotalEnzymes'] = sgpt + sgot
        model_input_data['AgeGroup'] = 0 if age < 30 else (1 if age < 50 else 2)
        model_input_data['LowProtein'] = 1 if tp < 6.0 else 0
        model_input_data['HighEnzymes'] = 1 if (sgpt > 40 or sgot > 40) else 0
        model_input_data['AgeGenderInteraction'] = age * gender
        
        feature_columns = [
            'Age', 'Gender', 'TB', 'DB', 'Alkphos', 'Sgpt', 'Sgot', 'TP', 'ALB', 
            'AGRatio', 'BilirubinRatio', 'SGPTSGOTRatio', 'TotalEnzymes', 
            'AgeGroup', 'LowProtein', 'HighEnzymes', 'AgeGenderInteraction'
        ]
        
        for col in feature_columns:
            if col not in model_input_data: model_input_data[col] = 0
        
        for key, value in model_input_data.items():
            try: model_input_data[key] = float(value) if value is not None else 0.0
            except: model_input_data[key] = 0.0
        
        df = pd.DataFrame([model_input_data], columns=feature_columns)
        probability = model.predict_proba(df)[0][1]
        return float(probability)
    except Exception as e:
        current_app.logger.error(f"Liver prediction error: {e}")
        raise ValueError("Failed to preprocess liver data.")

def predict_mental_health(data: Dict[str, Any]) -> float:
    model = models.get('mental_health')
    if model is None:
        current_app.logger.error("Mental Health model is not loaded.")
        raise RuntimeError("Mental Health model is not loaded.")
        
    try:
        feature_columns = ['phq_score', 'gad_score', 'depressiveness', 'suicidal', 'anxiousness', 'sleepiness', 'age', 'gender']
        data['gender'] = 1 if data.get('gender') == 'Male' else 0
        for col in ['depressiveness', 'suicidal', 'anxiousness', 'sleepiness']:
            data[col] = 1 if data.get(col) else 0

        df = pd.DataFrame([data], columns=feature_columns)
        try:
            probability = model.predict_proba(df)[0][1]
            return float(probability)
        except Exception:
            risk_score = 0.0
            phq = data.get('phq_score', 0)
            gad = data.get('gad_score', 0)
            if phq >= 10: risk_score += 0.4
            elif phq >= 5: risk_score += 0.2
            if gad >= 10: risk_score += 0.3
            elif gad >= 5: risk_score += 0.15
            if data.get('suicidal'): risk_score += 0.3
            if data.get('depressiveness'): risk_score += 0.2
            if data.get('anxiousness'): risk_score += 0.2
            if data.get('sleepiness'): risk_score += 0.1
            return float(min(risk_score, 1.0))
    except Exception as e:
        current_app.logger.error(f"Mental Health prediction error: {e}")
        raise ValueError("Failed to preprocess mental health data.")

def run_prediction(assessment_type: str, input_data: dict) -> float:
    if assessment_type == 'diabetes': return predict_diabetes(input_data)
    elif assessment_type == 'heart': return predict_heart(input_data)
    elif assessment_type == 'liver': return predict_liver(input_data)
    elif assessment_type == 'mental_health': return predict_mental_health(input_data)
    else: raise ValueError("Invalid assessment type")

def get_gemini_recommendations(risk_map: dict) -> List[Dict[str, Any]]:
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key: return {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        risk_summary = []
        for disease, level in risk_map.items():
            if level in ['Medium', 'High']:
                risk_summary.append(f"- {disease.replace('_risk_level', '').capitalize()}: {level} risk")

        prompt_intro = "A patient has health risks:\n" + "\n".join(risk_summary) if risk_summary else "Patient has Low risk."
        prompt = f"""You are a medical assistant. {prompt_intro} Give lifestyle advice in JSON list format with keys: disease_type, category, recommendation_text, risk_level. Categories: Immediate Action, Dietary Plan, Habit Change, Wellness. Format: Only JSON list."""
        
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        recommendations = json.loads(cleaned_text)
        grouped_recs = {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}
        for rec in recommendations:
            cat = rec.get("category", "Lifestyle").lower()
            if cat in grouped_recs: grouped_recs[cat].append(rec)
            else: grouped_recs["lifestyle"].append(rec)
        return grouped_recs
    except Exception: return {"diet": [], "exercise": [], "sleep": [], "lifestyle": []}

def get_chatbot_response(message: str, history: List[Dict[str, str]] = None) -> str:
    """Generates a response from the AI medical assistant chatbot."""
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key: return "I'm sorry, my medical intelligence system is currently offline."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        system_instruction = "You are 'PreventVance AI', a medical assistant. Help with risks, care advice, and platform features. Don't diagnose. Urge ER for emergencies."
        formatted_history = []
        if history:
            for entry in history:
                role = "user" if entry.get("role") == "user" else "model"
                formatted_history.append({"role": role, "parts": [entry.get("content", "")]})

        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(f"SYSTEM: {system_instruction}\nUSER: {message}")
        return response.text
    except Exception as e:
        current_app.logger.error(f"Chatbot error: {e}")
        return "I encountered an error processing your request."