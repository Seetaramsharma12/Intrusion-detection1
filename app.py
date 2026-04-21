from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import os
import time

app = Flask(__name__)
CORS(app)

# Load Model
MODEL_PATH = 'model/isolation_forest.pkl'
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
    else:
        print("Model file not found. Please train the model first.")

load_model()

# Global stats storage (in-memory for demo)
stats = {
    'total_requests': 0,
    'threats_blocked': 0,
    'active_threats': 0,
    'history': [] # List of recent 50 requests
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": model is not None})

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Receives packet data: { packet_size, duration, request_rate, protocol_type }
    Returns: { status: "allowed" | "blocked", confidence: float }
    """
    global stats
    
    if not model:
        return jsonify({"error": "Model not loaded"}), 500
        
    data = request.json
    try:
        # Preprocess
        # protocol_type might need mapping if sent as string, for now expect int
        # Features must match training: ['packet_size', 'duration', 'request_rate', 'protocol_type']
        features = [
            float(data.get('packet_size', 0)),
            float(data.get('duration', 0)),
            float(data.get('request_rate', 0)),
            float(data.get('protocol_type', 0))
        ]
        
        # Predict (-1 is anomaly, 1 is normal)
        prediction = model.predict([features])[0]
        
        timestamp = time.strftime("%H:%M:%S")
        stats['total_requests'] += 1
        
        result = "allowed"
        if prediction == -1:
            result = "blocked"
            stats['threats_blocked'] += 1
            stats['active_threats'] += 1 # Just incrementing for demo effect
        
        # Log to history
        log_entry = {
            "timestamp": timestamp,
            "ip": data.get("ip", "192.168.1.100"), # Mock IP
            "type": "Malicious" if result == "blocked" else "Normal",
            "action": "Blocked" if result == "blocked" else "Allowed",
            "details": f"Size: {features[0]} | Rate: {features[2]}"
        }
        stats['history'].insert(0, log_entry)
        if len(stats['history']) > 50:
            stats['history'].pop()
            
        return jsonify({
            "status": result,
            "prediction": int(prediction),
            "log": log_entry
        })
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
