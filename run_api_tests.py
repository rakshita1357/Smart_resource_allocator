from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine
from app.db.base import Base

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

print('Testing volunteer registration...')
payload = {
    "name": "Riya Sharma",
    "email": "riya@example.com",
    "phone": "9876543210",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "skills": ["medical", "first aid"],
    "availability": "weekends",
    "experience_level": "beginner",
}
resp = client.post('/volunteer/register', json=payload)
print('Status:', resp.status_code)
try:
    print('Response:', resp.json())
except Exception as e:
    print('No JSON response:', e)

print('\nTesting survey upload endpoint...')
# Minimal PNG header bytes; endpoint only saves and runs OCR which may return empty
files = {'file': ('test.png', b'\x89PNG\r\n\x1a\n', 'image/png')}
resp2 = client.post('/survey/upload', files=files)
print('Status:', resp2.status_code)
try:
    print('Response:', resp2.json())
except Exception as e:
    print('No JSON response:', e)

