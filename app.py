import os
import tempfile
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

# Import the Class from your processor.py
from processor import DocumentProcessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize the processor once at the global level
processor = DocumentProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if file:
        filename = secure_filename(file.filename)
        
        # Create a temporary directory to store the file for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            try:
                # 1. Use the class instance to process the document
                # This returns a Pydantic object (DocumentResponse)
                result_obj = processor.process(file_path)
                
                # 2. Convert Pydantic object to a dictionary for Flask's jsonify
                # .model_dump() is the Pydantic v2 way to get a dict
                return jsonify(result_obj.model_dump())
            
            except Exception as e:
                return jsonify({
                    'error': 'Critical processing failure',
                    'details': str(e)
                }), 500

if __name__ == '__main__':
    # Ensure GEMINI_API_KEY is available
    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: No API Key found in environment variables!")
        
    app.run(debug=True, port=5000)