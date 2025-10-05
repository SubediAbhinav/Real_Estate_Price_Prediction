import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app



import pytest
from models.user import User
from models import db

# ==========================
# Fixture for test client
# ==========================
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # in-memory DB
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

# ==========================
# Test registration
# ==========================
def test_registration(client):
    # Correct registration data
    response = client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'abhinav1@example.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    # Missing name
    response = client.post('/auth/register', data={
        'name': '',
        'email': 'samir2@example.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert b"Name cannot be empty" in response.data

    # Invalid email
    response = client.post('/auth/register', data={
        'name': 'Test User 2',
        'email': 'samir1.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert b"Invalid email format" in response.data

    # Short password
    response = client.post('/auth/register', data={
        'name': 'User 4',
        'email': 'user4@example.com',
        'password': '123'
    }, follow_redirects=True)
    assert b"Password must be at least 6 characters" in response.data

# ==========================
# Test login
# ==========================
def test_login(client):
    # First, create a user
    with app.app_context():
        user = User(name="Test User", email="abhinav1@example.com")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

    # Correct login
    response = client.post('/auth/login', data={
        'email': 'abhinav1@example.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Login successful" in response.data

    # Incorrect password
    response = client.post('/auth/login', data={
        'email': 'abhinav1@example.com',
        'password': 'WrongPass'
    }, follow_redirects=True)
    assert b"Invalid email or password" in response.data

    # Invalid email format
    response = client.post('/auth/login', data={
        'email': 'samir1.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert b"Invalid email format" in response.data

    # Non-existent user
    response = client.post('/auth/login', data={
        'email': 'samir1@example.com',
        'password': 'Password123'
    }, follow_redirects=True)
    assert b"Invalid email or password" in response.data
