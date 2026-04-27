from tests.conftest import unique_phone

def test_create_employee(auth_client, faker):
    first_name = faker.first_name()
    last_name = faker.last_name()
    email = faker.email()
    phone = unique_phone()
    
    emp_data = {
        "FirstName": first_name,
        "LastName": last_name,
        "Email": email,
        "Phone": phone,
        "is_active": True
    }
    response = auth_client.post("/employees/", json=emp_data)
    assert response.status_code == 201
    data = response.json()
    assert data["FirstName"] == first_name
    assert data["Phone"] == phone
    assert "EmpId" in data

def test_read_employees(auth_client, faker):
    # First create an employee with a guaranteed unique phone
    name = faker.first_name()
    auth_client.post("/employees/", json={
        "FirstName": name,
        "LastName": faker.last_name(),
        "Email": faker.email(),
        "Phone": unique_phone(),
        "is_active": True
    })
    
    response = auth_client.get("/employees/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(emp["FirstName"] == name for emp in data)
