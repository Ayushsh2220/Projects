# create_recruiter_user.py
from utils.recruiter_db import register_user, init_recruiter_db

# 🔧 Initialize the recruiter database (if not already created)
init_recruiter_db()

# 🧑 Add new users manually
users = [
    {"username": "admin", "password": "admin123", "email": "admin1@gmail.com", "role": "admin"},
    {"username": "recruiter1", "password": "recpass1", "email": "rec1@example.com", "role": "recruiter"},
    {"username": "recruiter2", "password": "recpass2", "email": "rec2@example.com", "role": "recruiter"},
]

for user in users:
    success = register_user(user["username"], user["password"], user["email"], user["role"])
    if success:
        print(f"{user['role'].capitalize()} '{user['username']}' created successfully!")
    else:
        print(f"⚠️ Username '{user['username']}' already exists.")
