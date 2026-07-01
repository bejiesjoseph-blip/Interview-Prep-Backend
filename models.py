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



    