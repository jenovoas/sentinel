from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_cors_preflight_allowed_origin():
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization",
    }
    response = client.options("/", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-credentials") == "true"

    # Verify explicitly allowed methods and headers
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allowed_methods

    allowed_headers = response.headers.get("access-control-allow-headers", "")
    assert "Content-Type" in allowed_headers or "content-type" in allowed_headers.lower()

def test_cors_preflight_disallowed_header():
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-Custom-Disallowed-Header",
    }
    response = client.options("/", headers=headers)
    # CORSMiddleware returns 400 Bad Request when request headers are not allowed
    assert response.status_code == 400

def test_cors_preflight_disallowed_method():
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "TRACE",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/", headers=headers)
    # CORSMiddleware returns 400 Bad Request when request method is not allowed
    assert response.status_code == 400
