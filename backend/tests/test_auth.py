from tests.conftest import unique_phone

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Login API is running"}

def test_register_user(client, faker):
    phone = unique_phone()
    name = faker.company()
    user_data = {
        "phone": phone,
        "name": name
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == phone
    assert data["name"] == name
    assert "company_id" in data

def test_duplicate_phone_rejected(client, faker):
    """Registering the same phone twice should return 400."""
    phone = unique_phone()
    name = faker.company()
    client.post("/register", json={"phone": phone, "name": name})
    response = client.post("/register", json={"phone": phone, "name": name})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
