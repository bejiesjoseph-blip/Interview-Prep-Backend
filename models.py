from config import db, cursor
from werkzeug.security import generate_password_hash, check_password_hash


def create_tables():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(150) UNIQUE,
        password VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        filename VARCHAR(255),
        resume_text LONGTEXT,
        structured_json LONGTEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        difficulty VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions(
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT,
        question TEXT,
        difficulty VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES interview_sessions(id)
    )
    """)



create_tables()

#Register User

def register_user(name, email, password):

    cursor.execute(
        "SELECT id FROM users WHERE email=%s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        return {
            "success": False,
            "message": "User already exists"
        }

    hashed_password = generate_password_hash(password)

    cursor.execute("""
    INSERT INTO users(name, email, password)
    VALUES(%s, %s, %s)
    """, (name, email, hashed_password))

    db.commit()

    return {
        "success": True,
        "message": "User registered successfully"
    }

#Login User

def login_user(email, password):

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user = cursor.fetchone()

    if not user:
        return None

    if check_password_hash(user["password"], password):
        return user

    return None

#save resume

from config import db, cursor
import json

def save_resume(user_id, filename, resume_text, structured_json):

    cursor.execute("""
    INSERT INTO resumes(
        user_id,
        filename,
        resume_text,
        structured_json
    )
    VALUES(%s, %s, %s, %s)
    """, (
        user_id,
        filename,
        resume_text,
        structured_json
    ))

    db.commit()

#Get Resume

def get_latest_resume(user_id):

    cursor.execute("""
    SELECT *
    FROM resumes
    WHERE user_id=%s
    ORDER BY id DESC
    LIMIT 1
    """, (user_id,))

    resume = cursor.fetchone()

    return resume


#Create Interview Session

def create_interview_session(user_id, difficulty):

    cursor.execute("""
    INSERT INTO interview_sessions(
        user_id,
        difficulty
    )
    VALUES(%s, %s)
    """, (
        user_id,
        difficulty
    ))

    db.commit()

    return cursor.lastrowid

#Save Questions

from config import db, cursor
def save_questions(session_id, questions, difficulty):

    for question in questions:

        cursor.execute("""
        INSERT INTO questions(
            session_id,
            question,
            difficulty
        )
        VALUES(%s, %s, %s)
        """, (
            session_id,
            question,
            difficulty
        ))

    db.commit()


#Historyy

def get_history(user_id):

    # Get all interview sessions for user
    cursor.execute("""
    SELECT *
    FROM interview_sessions
    WHERE user_id=%s
    ORDER BY id DESC
    """, (user_id,))

    sessions = cursor.fetchall()

    history = []

    for session in sessions:

        # Get questions for each session
        cursor.execute("""
        SELECT question, difficulty
        FROM questions
        WHERE session_id=%s
        """, (session["id"],))

        questions = cursor.fetchall()

        history.append({
            "session_id": session["id"],
            "difficulty": session["difficulty"],
            "created_at": str(session["created_at"]),
            "questions": questions
        })

    return history
    