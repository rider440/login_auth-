from tests.conftest import unique_phone


def test_create_task(auth_client, faker):
    task_name = faker.sentence(nb_words=3)
    task_data = {
        "TaskName": task_name,
        "description": faker.paragraph(),
        "status": "Pending",
        "priority": "High"
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["TaskName"] == task_name
    assert "TaskId" in data


def test_assign_task(auth_client, faker):
    # Create employee with a guaranteed-unique phone
    emp_resp = auth_client.post("/employees/", json={
        "FirstName": faker.first_name(),
        "LastName": faker.last_name(),
        "Email": faker.email(),
        "Phone": unique_phone()
    })
    emp_id = emp_resp.json()["EmpId"]

    # Create task
    task_resp = auth_client.post("/tasks/", json={
        "TaskName": faker.sentence(nb_words=3),
        "description": faker.paragraph(),
        "status": "Pending",
        "priority": "Low"
    })
    task_id = task_resp.json()["TaskId"]

    # Assign task to employee
    response = auth_client.post("/tasks/assign/", json={
        "task_id": task_id,
        "emp_id": emp_id
    })
    assert response.status_code == 201
    assert response.json()["task_id"] == task_id
    assert response.json()["emp_id"] == emp_id


def test_update_task_status(auth_client, faker):
    """Updating a task's status should reflect in the response."""
    task_resp = auth_client.post("/tasks/", json={
        "TaskName": faker.sentence(nb_words=3),
        "description": faker.paragraph(),
        "status": "Pending",
        "priority": "Normal"
    })
    task_id = task_resp.json()["TaskId"]

    response = auth_client.put(f"/tasks/{task_id}", json={"status": "In Progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
