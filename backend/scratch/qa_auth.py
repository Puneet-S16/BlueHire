import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
import time
from fastapi.testclient import TestClient
from main import app
from db.session import SessionLocal
from models.user import User

client = TestClient(app)

def run_qa():
    print("Starting QA Validation...")
    results = {"PASS": 0, "FAIL": 0, "BUGS": [], "WARNINGS": []}
    
    def assert_eq(name, actual, expected, context=""):
        if actual == expected:
            print(f"[PASS] {name}")
            results["PASS"] += 1
        else:
            print(f"[FAIL] {name} | Expected: {expected} | Actual: {actual} | {context}")
            results["FAIL"] += 1
            results["BUGS"].append(f"{name} failed. Actual: {actual}")
    
    def assert_in(name, text, container, context=""):
        if text in container:
            print(f"[PASS] {name}")
            results["PASS"] += 1
        else:
            print(f"[FAIL] {name} | Expected '{text}' in response | {context}")
            results["FAIL"] += 1
            results["BUGS"].append(f"{name} failed.")
            
    # Clean up any existing test user
    test_email = "qa_test_user@example.com"
    db = SessionLocal()
    db.query(User).filter(User.email == test_email).delete()
    db.commit()
    
    # 1. User Signup
    print("\n--- 1. User Signup ---")
    
    payload = {
        "email": test_email,
        "password": "StrongPassword123!",
        "confirm_password": "StrongPassword123!",
        "role": "WORKER",
        "accept_terms": True
    }
    r = client.post("/api/v1/auth/signup", json=payload)
    if r.status_code != 201:
        print("Signup 422 error:", r.json())
    assert_eq("Valid signup status", r.status_code, 201)
    
    r = client.post("/api/v1/auth/signup", json=payload)
    assert_eq("Duplicate email status", r.status_code, 409)
    
    invalid_email_payload = {**payload, "email": "not-an-email"}
    r = client.post("/api/v1/auth/signup", json=invalid_email_payload)
    assert_eq("Invalid email status", r.status_code, 422)
    
    weak_pwd_payload = {**payload, "email": "test2@example.com", "password": "weak", "confirm_password": "weak"}
    r = client.post("/api/v1/auth/signup", json=weak_pwd_payload)
    assert_eq("Weak password status", r.status_code, 422)
    
    mismatch_payload = {**payload, "email": "test3@example.com", "password": "StrongPassword123!", "confirm_password": "Different123!"}
    r = client.post("/api/v1/auth/signup", json=mismatch_payload)
    assert_eq("Password mismatch status", r.status_code, 422)
    
    no_terms_payload = {**payload, "email": "test4@example.com", "accept_terms": False}
    r = client.post("/api/v1/auth/signup", json=no_terms_payload)
    assert_eq("Terms not accepted status", r.status_code, 422)
    
    # 2. Login
    print("\n--- 2. Login ---")
    
    login_payload = {"email": test_email, "password": "StrongPassword123!"}
    r = client.post("/api/v1/auth/login", json=login_payload)
    assert_eq("Correct login status", r.status_code, 200)
    tokens = r.json() if r.status_code == 200 else {}
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    
    wrong_pwd_payload = {"email": test_email, "password": "WrongPassword123!"}
    r = client.post("/api/v1/auth/login", json=wrong_pwd_payload)
    assert_eq("Wrong password status", r.status_code, 401)
    
    non_email_payload = {"email": "doesnotexist@example.com", "password": "StrongPassword123!"}
    r = client.post("/api/v1/auth/login", json=non_email_payload)
    assert_eq("Non-existent email status", r.status_code, 401)
    
    # Inactive user
    user = db.query(User).filter(User.email == test_email).first()
    if user:
        user.is_active = False
        db.commit()
    r = client.post("/api/v1/auth/login", json=login_payload)
    assert_eq("Inactive user login status", r.status_code, 403)
    
    if user:
        user.is_active = True
        db.commit()
        
    r = client.post("/api/v1/auth/login", json=login_payload)
    tokens = r.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
        
    # 3. JWT & 4. Protected Routes
    print("\n--- 3. & 4. JWT and Protected Routes ---")
    
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert_eq("Valid JWT on /auth/me", r.status_code, 200)
    if r.status_code == 200:
        assert_eq("Valid JWT email match", r.json()["email"], test_email)
        
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert_eq("Invalid JWT on /auth/me", r.status_code, 401)
    
    r = client.get("/api/v1/auth/me")
    assert_eq("Missing JWT on /auth/me", r.status_code, 401)
    
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert_eq("Wrong token type on /auth/me", r.status_code, 401)
    
    print("\n--- Token Refresh ---")
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert_eq("Valid refresh token status", r.status_code, 200)
    if r.status_code == 200:
        new_tokens = r.json()
        new_access = new_tokens.get("access_token")
        new_refresh = new_tokens.get("refresh_token")
    else:
        new_access = access_token
        new_refresh = refresh_token
        
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.refresh.token"})
    assert_eq("Invalid refresh token status", r.status_code, 401)
    
    # 5. Password Change
    print("\n--- 5. Password Change ---")
    
    r = client.post("/api/v1/auth/change-password", headers={"Authorization": f"Bearer {new_access}"}, json={
        "current_password": "WrongPassword123!",
        "new_password": "NewStrongPassword123!",
        "confirm_password": "NewStrongPassword123!"
    })
    assert_eq("Change password wrong current", r.status_code, 401)
    
    r = client.post("/api/v1/auth/change-password", headers={"Authorization": f"Bearer {new_access}"}, json={
        "current_password": "StrongPassword123!",
        "new_password": "weak",
        "confirm_password": "weak"
    })
    assert_eq("Change password weak new", r.status_code, 422)
    
    r = client.post("/api/v1/auth/change-password", headers={"Authorization": f"Bearer {new_access}"}, json={
        "current_password": "StrongPassword123!",
        "new_password": "NewStrongPassword123!",
        "confirm_password": "NewStrongPassword123!"
    })
    assert_eq("Successful password change", r.status_code, 200)
    
    # 6. Logout
    print("\n--- 6. Logout ---")
    r = client.post("/api/v1/auth/logout", json={"refresh_token": new_refresh})
    assert_eq("Valid logout status", r.status_code, 200)
    
    r = client.post("/api/v1/auth/logout", json={"refresh_token": "invalid.token"})
    assert_eq("Invalid refresh token logout status", r.status_code, 200) 
    
    # 7. Swagger
    print("\n--- 7. Swagger ---")
    r = client.get("/api/v1/openapi.json")
    assert_eq("OpenAPI json status", r.status_code, 200)
    if r.status_code == 200:
        schema = r.json()
        paths = schema.get("paths", {})
        assert_in("Swagger /auth/signup", "/api/v1/auth/signup", paths)
        assert_in("Swagger /auth/login", "/api/v1/auth/login", paths)
        assert_in("Swagger /auth/refresh", "/api/v1/auth/refresh", paths)
        assert_in("Swagger /auth/logout", "/api/v1/auth/logout", paths)
        assert_in("Swagger /auth/change-password", "/api/v1/auth/change-password", paths)
        assert_in("Swagger /auth/me", "/api/v1/auth/me", paths)
        
    print("\n====================")
    print(f"Results: {results['PASS']} PASS, {results['FAIL']} FAIL")
    if results["BUGS"]:
        print("BUGS:")
        for b in results["BUGS"]:
            print(f"- {b}")

if __name__ == "__main__":
    run_qa()
