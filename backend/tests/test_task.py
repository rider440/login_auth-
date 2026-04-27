def test_create_task(auth_client):
    task_data = {
        "TaskName": "Test Task",
        "description": "This is a test task",
        "status": "Pending",
        "priority": "High"
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["TaskName"] == "Test Task"
    assert "TaskId" in data

def test_assign_task(auth_client):
    # Create employee
    emp_resp = auth_client.post("/employees/", json={
        "FirstName": "Worker",
        "LastName": "One",
        "Email": "worker.one@example.com",
        "Phone": "7777777777"
    })
    emp_id = emp_resp.json()["EmpId"]
    
    # Create task
    task_resp = auth_client.post("/tasks/", json={
        "TaskName": "Assigned Task",
        "description": "Task to be assigned",
        "status": "Pending",
        "priority": "Low"
    })
    task_id = task_resp.json()["TaskId"]
    
    # Assign task
    assign_data = {
        "task_id": task_id,
        "emp_id": emp_id
    }
    response = auth_client.post("/tasks/assign/", json=assign_data)
    assert response.status_code == 201
    assert response.json()["task_id"] == task_id
    assert response.json()["emp_id"] == emp_id
