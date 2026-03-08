# 🩺 Medical Report Simplifier

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Framework](https://img.shields.io/badge/framework-Flask%20%7C%20Streamlit-orange)

### Convert complex medical reports into clear, patient-friendly explanations.

This application ingests medical reports (PDF format), extracts the text, and leverages **Google Gemini 2.5 Flash** to translate complex medical jargon into easy-to-understand explanations. It also features an integrated medical chatbot for context-aware follow-up questions.

Ideal for patients, students, and clinicians seeking instant clarify on medical documentation.

---

## 🚀 Features

- **PDF Text Extraction**: Uses `pdfplumber` to accurately retrieve text from medical PDFs.
- **Medical Text Simplification**: Patient-friendly, student-level, or clinical bullet-point summaries powered by **Google Gemini 2.5 Flash**.
- **Adjustable Output Controls**: Choose conciseness (Short, Medium, Detailed) and output format (Summary Only, Key Findings, Full Explanation).
- **Integrated Medical Chatbot 🤖**: Ask context-aware follow-up questions about the specific report (e.g. "What does lymphovascular invasion mean?").
- **Downloadable Summary**: Export the simplified explanation as a `.txt` file.

---

## 🧠 System Architecture

The project utilizes a two-tier architecture:
- **Backend**: A Python Flask REST API responsible for PDF processing and LLM integration.
- **Frontend**: A Streamlit UI providing an intuitive experience for end-users.

```text
📁 Medical-Report-Simplifier
├── backend/
│   └── app.py               # Flask REST API endpoints
├── frontend/
│   └── app.py               # Streamlit user interface
├── files/                   # Sample reports and temporary files
├── .env.example             # Template for environment variables
├── .gitignore               # Ignored files (secrets, environments, temp)
├── requirements.txt         # Project dependencies
├── run.sh                   # Startup bootstrap script
└── README.md
```

---

## 📡 API Endpoints

### `POST /simplify`
Simplifies an uploaded medical PDF.
- **Payload (Form-Data)**:
  - `file`: PDF document
  - `conciseness`: Short / Medium / Detailed
  - `format`: Summary Only / Key Findings / Full Explanation
  - `level`: patient / student / clinician
- **Response**: `{"simplified_text": "..."}`

### `POST /chat_followup`
Answers questions based on the simplified report context.
- **Payload (Form-Data)**:
  - `question`: User's follow-up question
  - `simplified_report`: The generated explanation
  - `chat_history`: Previous conversation context
- **Response**: `{"answer": "..."}`

---

## 🧪 Local Setup & Installation

### Prerequisites
- Python 3.9+
- A Google Gemini API Key

### Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yoogendra/medical-report-simplifier.git
   cd medical-report-simplifier
   ```

2. **Run the Initialization Script**
   For Unix-based systems (Linux/macOS), you can bootstrap the environment and start the application with a single command:
   ```bash
   ./run.sh
   ```
   > **Note:** The script will automatically create a `.env` file from the `.env.example` template on the first run.

3. **Configure Environment Variables**
   Open the newly created `.env` file in the root directory and add your secret tokens:
   ```ini
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   BACKEND_URL=http://127.0.0.1:5000
   ```

4. **Restart the Application**
   Run the startup script again. It will automatically initialize both the Flask backend and the Streamlit frontend.
   ```bash
   ./run.sh
   ```
   - **Frontend**: Available at `http://localhost:8501`
   - **Backend**: Available at `http://127.0.0.1:5000`