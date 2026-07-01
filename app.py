import re

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.utils import secure_filename
import os
import json
import pdfplumber

from config import gemini_model
from models import (
    register_user,
    login_user,
    save_resume,
    get_latest_resume,
    create_interview_session,
    save_questions,
    get_history
)

app = Flask(__name__)

# JWT CONFIG

app.config["JWT_SECRET_KEY"] = "my_super_secret_key_for_ai_interview_backend_2026"
jwt = JWTManager(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HOME

@app.route("/")
def home():
    return jsonify({
        "message": "AI Interview Preparation Backend Running"
    })


# REGISTER

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    result = register_user(name, email, password)

    return jsonify(result)

# LOGIN

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = login_user(email, password)

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user["id"]))

    return jsonify({
        "message": "Login Successful",
        "token": token
    })

# PDF TEXT EXTRACTION

def extract_text(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

# UPLOAD RESUME

@app.route("/upload-resume", methods=["POST"])
@jwt_required()
def upload_resume():

    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "PDF file required"}), 400

    file = request.files["file"]

    filename = secure_filename(file.filename)

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    resume_text = extract_text(filepath)

    prompt = f"""
Extract the resume.

Return ONLY a JSON object.

Do NOT use markdown.

Do NOT use ```.

Schema:

{{
    "name":"",
    "skills":[],
    "projects":[],
    "experience":[],
    "education":[]
}}

Resume:

{resume_text}
"""
    import re

    response = gemini_model.generate_content(prompt)
   

    structured_resume = response.text.strip()

    structured_resume = re.sub(r"^```json\s*", "", structured_resume)
    structured_resume = re.sub(r"^```\s*", "", structured_resume)
    structured_resume = re.sub(r"\s*```$", "", structured_resume)

    print("Cleaned Json:")
    print(structured_resume)


    
    resume_json = json.loads(structured_resume)

    save_resume(
        user_id=user_id,
        filename=filename,
        resume_text=resume_text,
        structured_json=structured_resume
    )

    return jsonify({
        "message": "Resume Uploaded Successfully",
        "resume": resume_json
    })


