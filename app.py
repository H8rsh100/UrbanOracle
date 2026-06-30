import os
import json
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from routes.hotspot import hotspot_bp

app = Flask(__name__)
app.register_blueprint(hotspot_bp)

# Load models and preprocessing objects on startup
models = {}
mlp_model = None
encoders = None
scaler = None

try:
    models['Logistic Regression'] = joblib.load('models/saved/logistic_regression.pkl')
    models['SVM'] = joblib.load('models/saved/svm.pkl')
    models['Decision Tree'] = joblib.load('models/saved/decision_tree.pkl')
    models['Random Forest'] = joblib.load('models/saved/random_forest.pkl')
    models['Multivariate Linear Regression'] = joblib.load('models/saved/multivariate_linear_regression.pkl')
    
    mlp_model = load_model('models/saved/mlp_model.h5')
    
    encoders = joblib.load('models/saved/encoders.pkl')
    scaler = joblib.load('models/saved/scaler.pkl')
    
    print("All models loaded successfully.")
except Exception as e:
    print(f"Warning: Not all models loaded. Have you run the training scripts? Error: {e}")

@app.route('/')
def index():
    districts = []
    locations = []
    crime_types = []
    if encoders:
        districts = encoders['District'].classes_.tolist()
        locations = encoders['Location Description'].classes_.tolist()
        crime_types = encoders['Primary Type'].classes_.tolist()
    return render_template('index.html', districts=districts, locations=locations, crime_types=crime_types)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.form
        
        # 'Hour', 'DayOfWeek', 'Month', 'District', 'Primary Type', 'Location Description', 'Domestic'
        hour = int(data.get('hour', 12))
        day = int(data.get('day_of_week', 3))
        month = int(data.get('month', 6))
        
        district_raw = data.get('district', '1')
        crime_type_raw = data.get('crime_type', 'THEFT')
        loc_desc_raw = data.get('location_desc', 'STREET')
        domestic = int(data.get('domestic', 0))

        # Encode categorical inputs
        # If input unseen, fallback to 0 safely
        district = encoders['District'].transform([district_raw])[0] if district_raw in encoders['District'].classes_ else 0
        crime_type = encoders['Primary Type'].transform([crime_type_raw])[0] if crime_type_raw in encoders['Primary Type'].classes_ else 0
        loc_desc = encoders['Location Description'].transform([loc_desc_raw])[0] if loc_desc_raw in encoders['Location Description'].classes_ else 0

        features = [[hour, day, month, district, crime_type, loc_desc, domestic]]
        features_scaled = scaler.transform(features)

        results = {}
        # Classical Classifiers
        for name in ['Logistic Regression', 'SVM', 'Decision Tree', 'Random Forest']:
            if name in models:
                prob = models[name].predict_proba(features_scaled)[0][1]
                results[name] = float(prob)
        
        # MLR
        if 'Multivariate Linear Regression' in models:
            risk = models['Multivariate Linear Regression'].predict(features_scaled)[0]
            results['Risk Score'] = float(risk)

        # MLP
        if mlp_model is not None:
            mlp_prob = mlp_model.predict(features_scaled)[0][0]
            results['MLP Neural Network'] = float(mlp_prob)

        # Feature Attribution calculation (Sensitivity analysis / LIME-like)
        attributions = {}
        if 'Random Forest' in models:
            rf_model = models['Random Forest']
            base_prob = rf_model.predict_proba(features_scaled)[0][1]
            feature_names = ['Hour', 'Day of Week', 'Month', 'District', 'Crime Type', 'Location Description', 'Domestic']
            for idx, f_name in enumerate(feature_names):
                perturbed_features = features_scaled.copy()
                perturbed_features[0][idx] = 0.0  # Set this feature to its mean
                perturbed_prob = rf_model.predict_proba(perturbed_features)[0][1]
                # Difference: positive means the input value increased arrest likelihood
                attributions[f_name] = float(base_prob - perturbed_prob)

        return jsonify({"status": "success", "predictions": results, "attributions": attributions})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/analytics', methods=['GET'])
def analytics():
    if os.path.exists('results.json'):
        with open('results.json', 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"error": "results.json not found"})

@app.route('/history', methods=['GET'])
def history():
    if os.path.exists('mlp_history.json'):
        with open('mlp_history.json', 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"error": "mlp_history.json not found"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
