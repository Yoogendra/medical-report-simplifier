import google.generativeai as genai
import logging
import os

class LLMService:
    def __init__(self):
        """
        Initializes the LLM Service and securely loads the API key from the environment.
        """
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logging.warning("GOOGLE_API_KEY environment variable not set. LLM features will fail.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")

    def generate_simplification(self, extracted_text: str, level: str, conciseness: str, output_format: str) -> str:
        """
        Receives extracted medical text and structured user preferences to build the prompt
        and hit the Gemini API for simplification. 
        """
        # Define instruction based on simplification level
        if level == "patient":
            base_instruction = "Explain this in simple, compassionate, patient-friendly language."
        elif level == "student":
            base_instruction = "Summarize this like a medical lecturer explaining key findings to a medical student."
        else:
            base_instruction = "Summarize this as tight, structured clinical bullet points for a clinician."

        prompt = f"""
You are an expert medical explanation assistant. {base_instruction} Simplify the following medical report EXACTLY according to the user's preferences.

=== USER SETTINGS ===
Simplification Level: {level}
Conciseness: {conciseness}
Format: {output_format}

=== HARD RULES (MUST FOLLOW) ===
1. If Conciseness = "Detailed":
   - Your output MUST be at least 8–12 paragraphs.
   - Include: what the diagnosis means, how it happens, symptoms, test interpretations, staging meaning, treatment plan, why that treatment is chosen, risks, prognosis, and emotional reassurance.
   - Use headers and subheaders.
   - NO summarizing. FULL explanation.

2. If Format = "Full Explanation":
   - Include: 
        • “Summary of Findings”
        • “What This Diagnosis Means”
        • “How Doctors Interpret the Tests”
        • “Does it Mean Cancer Spread?”
        • “Treatment Options & Why They Are Chosen”
        • “Prognosis”
        • “Supportive Guidance”
   - Write in a warm, empathetic tone.
   - Expand each section into multiple sentences and paragraphs.

3. If Format = "Summary Only":
   - MAXIMUM 5 sentences.

4. If Format = "Summary + Key Findings":
   - 1 short paragraph + 6–10 bullet points.

5. Do NOT add new medical information not found in the report.
6. Be strictly medically accurate.
7. Do NOT compress the explanation if conciseness = Detailed.

=== MEDICAL REPORT TO EXPLAIN ===
{extracted_text}

Now produce the explanation.
"""
        response = self.model.generate_content(prompt)
        return response.text

    def generate_chat_response(self, user_question: str, simplified_report: str, chat_history: str) -> str:
        """
        Generates a context-aware answer to a user's follow-up question based on their report.
        """
        prompt = f"""
You are a medical assistant chatbot helping a patient understand THEIR OWN medical report.

Below is the simplified report of THEIR condition:
------------------------------------
{simplified_report}
------------------------------------

Conversation so far:
{chat_history}

User's new question:
{user_question}

Rules:
- Answer ONLY using information from their report.
- If user asks something not in the report, say:
  "Your report does not contain this information. Please consult your doctor."
- Be supportive and patient-friendly.
- Do NOT give medical advice, diagnoses, or treatment decisions.
- Focus on explanations, meaning, clarity, and reassurance.
- Keep answers short, clear, and easy to understand.

Now respond to the user's question.
"""
        response = self.model.generate_content(prompt)
        return response.text
