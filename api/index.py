import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Together AI API Configuration
TOGETHER_API_KEY = '07589fb47c69da2f5af8b4ecdee9b843614c5f76605e1706b1af22ea1dd728cd'
TOGETHER_API_ENDPOINT = 'https://api.together.xyz/v1/chat/completions'

def analyze_text_with_together_ai(text, prompt, language):
    """
    Analyze text using Together AI API
    
    Args:
        text (str): The text or code to analyze
        prompt (str, optional): Custom prompt for analysis
        language (str, optional): Programming language or text type
    
    Returns:
        dict: Analysis results
    """
    try:
        # Construct the full prompt if not provided
        if not prompt:
            prompt = f"Analyze this {language} code: \"{text}\"\n\nProvide a comprehensive analysis of the code."
        
        # Prepare API request payload
        payload = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful code and text analysis assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<｜end▁of▁sentence｜>"],
            "stream": False
        }
        
        # Headers for API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TOGETHER_API_KEY}'
        }
        
        # Make API request
        response = requests.post(TOGETHER_API_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        
        # Extract analysis from API response
        result = response.json()
        analysis = result['choices'][0]['message']['content']
        
        return {
            'status': 'success',
            'analysis': analysis,
            'source': 'Together AI API'
        }
    
    except requests.RequestException as e:
        return {
            'status': 'error',
            'message': f'API request failed: {str(e)}',
            'source': 'Together AI API'
        }

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    """
    Flask route to handle text analysis requests
    """
    try:
        # Get request data
        data = request.json
        text = data.get('text', '')
        prompt = data.get('prompt', '')
        language = data.get('language', 'unknown')
        
        # Validate input
        if not text:
            return jsonify({
                'status': 'error', 
                'message': 'No text provided for analysis'
            }), 400
        
        # Perform analysis
        result = analyze_text_with_together_ai(text, prompt, language)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

# Optional: Fallback mock analysis for testing
def mock_analyze_text(text, prompt=None, language=None):
    """
    Provide a mock analysis when API fails
    """
    return {
        'status': 'mock',
        'analysis': f"Mock analysis for {language} text:\n\n"
                    f"Text preview: {text[:100]}...\n\n"
                    "Note: This is a mock analysis due to API failure.",
        'source': 'Mock Fallback'
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
