"""
REST API for real-time fraud scoring of insurance claims.
"""

from flask import Flask, request, jsonify
from fraud_detector import FraudDetector
import os
import json

app = Flask(__name__)

# Initialize fraud detector
model_path = os.getenv('FRAUD_MODEL_PATH', 'fraud_detection_model.pkl')
detector = None

def load_detector():
    """Load fraud detection model."""
    global detector
    if detector is None:
        try:
            detector = FraudDetector(model_path=model_path)
            print(f"Fraud detection model loaded from {model_path}")
        except Exception as e:
            print(f"Warning: Could not load model: {e}")
            print("API will return mock responses until model is loaded")
    return detector

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    detector = load_detector()
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector is not None
    })

@app.route('/score', methods=['POST'])
def score_claim():
    """
    Score a claim for fraud risk.
    
    Request body should contain claim data as JSON.
    """
    detector = load_detector()
    
    if detector is None:
        # Return mock response if model not loaded
        return jsonify({
            'fraud_score': 45.0,
            'fraud_probability': 0.45,
            'prediction': 'Legitimate',
            'risk_level': 'Low',
            'warning': 'Model not loaded - returning mock response'
        })
    
    try:
        claim_data = request.get_json()
        
        if not claim_data:
            return jsonify({'error': 'No claim data provided'}), 400
        
        # Score claim
        result = detector.detect_fraud(claim_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/explain', methods=['POST'])
def explain_prediction():
    """
    Explain fraud prediction for a claim.
    
    Request body should contain claim data as JSON.
    """
    detector = load_detector()
    
    if detector is None:
        return jsonify({
            'error': 'Model not loaded',
            'fallback': {
                'method': 'Mock',
                'factors': [
                    {'factor': 'Claim Amount', 'impact': 'Normal range'}
                ]
            }
        })
    
    try:
        claim_data = request.get_json()
        method = request.args.get('method', 'shap')
        
        if not claim_data:
            return jsonify({'error': 'No claim data provided'}), 400
        
        # Get explanation
        explanation = detector.explain_prediction(claim_data, method=method)
        
        return jsonify(explanation)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch', methods=['POST'])
def batch_score():
    """
    Score multiple claims in batch.
    
    Request body should contain array of claim data.
    """
    detector = load_detector()
    
    if detector is None:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        claims = request.get_json()
        
        if not isinstance(claims, list):
            return jsonify({'error': 'Expected array of claims'}), 400
        
        results = []
        for claim in claims:
            result = detector.detect_fraud(claim)
            result['claim_id'] = claim.get('claim_id', 'unknown')
            results.append(result)
        
        return jsonify({
            'total_claims': len(results),
            'results': results,
            'summary': {
                'high_risk': sum(1 for r in results if r['risk_level'] == 'High'),
                'medium_risk': sum(1 for r in results if r['risk_level'] == 'Medium'),
                'low_risk': sum(1 for r in results if r['risk_level'] == 'Low')
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Fraud Scoring API...")
    print("Endpoints:")
    print("  POST /score - Score a single claim")
    print("  POST /explain - Explain prediction for a claim")
    print("  POST /batch - Score multiple claims")
    print("  GET /health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

