import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from starlette.testclient import TestClient
from app import app

client = TestClient(app)

# 1. Root route
r_root = client.get("/")
assert r_root.status_code == 200, f"Root returned {r_root.status_code}"
assert "DocuLens Enterprise AI" in r_root.text, "DocuLens title missing from root"
assert "authGateView" in r_root.text, "authGateView missing from root"
print("[PASS] GET / -> 200 OK (Full Modern UI)")

# 2. /static/index.html route (User's screenshot 3 error)
r_static = client.get("/static/index.html")
assert r_static.status_code == 200, f"/static/index.html returned {r_static.status_code}"
assert "authGateView" in r_static.text
print("[PASS] GET /static/index.html -> 200 OK (Resolved 404!)")

# 3. /studio route
r_studio = client.get("/studio")
assert r_studio.status_code == 200
print("[PASS] GET /studio -> 200 OK")

# 4. /modern route
r_modern = client.get("/modern")
assert r_modern.status_code == 200
print("[PASS] GET /modern -> 200 OK")

# 5. /static/app.js route
r_js = client.get("/static/app.js")
assert r_js.status_code == 200
assert "enterStudio" in r_js.text
print("[PASS] GET /static/app.js -> 200 OK")

# 6. /api/auth/login
r_login = client.post("/api/auth/login", json={"username": "auditor", "password": "auditor123"})
assert r_login.status_code == 200, f"Login failed: {r_login.text}"
data = r_login.json()
token = data["token"]
assert token, "Token not returned"
print(f"[PASS] POST /api/auth/login -> 200 OK (Token issued for {data['user']['username']})")

# 7. /api/documents
r_docs = client.get("/api/documents", headers={"Authorization": f"Bearer {token}"})
assert r_docs.status_code == 200
docs_data = r_docs.json()
print(f"[PASS] GET /api/documents -> 200 OK ({docs_data['count']} documents authorized for {docs_data['user']})")

# 8. /api/system-status
r_status = client.get("/api/system-status")
assert r_status.status_code == 200
print(f"[PASS] GET /api/system-status -> 200 OK")

print("\nALL SPACE ROUTE TESTS PASSED!")
