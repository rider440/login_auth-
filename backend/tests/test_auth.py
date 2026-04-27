def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Login API is running"}

def test_register_user(client):
    user_data = {
        "phone": "1234567890",
        "name": "Test User"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == "1234567890"
    assert data["name"] == "Test User"
    assert "company_id" in data
