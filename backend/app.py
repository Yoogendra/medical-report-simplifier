import os
import uuid
import logging
from flask import Flask, request, jsonify
import traceback

from services.llm_service import LLMService
from utils.pdf_extractor import extract_text_from_pdf

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize AI Service securely via environment variable
llm_service = LLMService()

# Ensure temp directory exists securely 
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/simplify", methods=["POST"])
def simplify():
    """
    Receives a medical PDF document, extracts text securely avoiding race conditions, 
    and returns a simplified LLM explanation.
    """
    tmp_path = None
    try:
        if "file" not in request.files:
            return jsonify({"error": "No PDF uploaded"}), 400

        uploaded_file = request.files["file"]
        
        # Prevent simultaneous write overwriting by using UUIDs
        safe_filename = f"{uuid.uuid4().hex}.pdf"
        tmp_path = os.path.join(UPLOAD_DIR, safe_filename)
        uploaded_file.save(tmp_path)

        # Extract text via utilities
        extracted_text = extract_text_from_pdf(tmp_path)
        if not extracted_text.strip():
            return jsonify({"error": "Could not extract text from PDF (Empty or Corrupted)"}), 400

        # Retrieve preferences
        level = request.form.get("level", "patient")
        conciseness = request.form.get("conciseness", "Medium")
        output_format = request.form.get("format", "Full Explanation")

        # Generate output through isolated service layer
        simplified = llm_service.generate_simplification(extracted_text, level, conciseness, output_format)

        return jsonify({"simplified_text": simplified})

    except Exception as e:
        logging.error(f"Simplify Error: {e}\n{traceback.format_exc()}")
        return jsonify({
            "error": "Internal Processing Error",
            "message": str(e)
        }), 500
    
    finally:
        # Secure Cleanup - delete temp UUID pdf to save space
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.route("/chat_followup", methods=["POST"])
def chat_followup():
    """
    Continues conversational medical inquiry using LLM Context mapping.
    """
    try:
        user_question = request.form.get("question")
        simplified_report = request.form.get("simplified_report")
        chat_history = request.form.get("chat_history", "")

        if not user_question:
            return jsonify({"error": "No question provided"}), 400

        answer = llm_service.generate_chat_response(user_question, simplified_report, chat_history)

        return jsonify({"answer": answer})

    except Exception as e:
        logging.error(f"Followup Chat Error: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal Chat Engine Error", "message": str(e)}), 500

if __name__ == "__main__":
    is_debug = os.getenv("FLASK_ENV") == "development"
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Backend API Mount => http://127.0.0.1:{port} (Debug: {is_debug})")
    app.run(host="127.0.0.1", port=port, debug=is_debug)
