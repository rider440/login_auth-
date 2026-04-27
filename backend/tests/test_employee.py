def test_create_employee(auth_client):
    emp_data = {
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john.doe@example.com",
        "Phone": "9876543210",
        "is_active": True
    }
    response = auth_client.post("/employees/", json=emp_data)
    assert response.status_code == 201
    data = response.json()
    assert data["FirstName"] == "John"
    assert data["Phone"] == "9876543210"
    assert "EmpId" in data

def test_read_employees(auth_client):
    # First create an employee
    auth_client.post("/employees/", json={
        "FirstName": "Jane",
        "LastName": "Smith",
        "Email": "jane.smith@example.com",
        "Phone": "8888888888",
        "is_active": True
    })
    
    response = auth_client.get("/employees/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(emp["FirstName"] == "Jane" for emp in data)
