def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_root(client):
    assert client.get("/").json()["service"] == "ClinicFlow API"


def test_metrics_exposed(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_create_appointment(client, appointment_payload):
    response = client.post("/api/appointments", json=appointment_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["patient_name"] == "Aarav Sharma"
    assert body["status"] == "SCHEDULED"


def test_create_appointment_validation_error(client, appointment_payload):
    response = client.post("/api/appointments", json={**appointment_payload, "patient_name": ""})
    assert response.status_code == 422
    response = client.post("/api/appointments", json={**appointment_payload, "status": "UNKNOWN"})
    assert response.status_code == 422


def test_list_and_get_appointment(client, appointment_payload):
    created = client.post("/api/appointments", json=appointment_payload).json()
    listed = client.get("/api/appointments").json()
    assert [a["id"] for a in listed] == [created["id"]]
    fetched = client.get(f"/api/appointments/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["doctor"] == "Dr. Mehta"


def test_get_missing_appointment_returns_404(client):
    response = client.get("/api/appointments/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"


def test_update_appointment_status(client, appointment_payload):
    created = client.post("/api/appointments", json=appointment_payload).json()
    response = client.put(f"/api/appointments/{created['id']}", json={"status": "CHECKED_IN"})
    assert response.status_code == 200
    assert response.json()["status"] == "CHECKED_IN"
    assert response.json()["patient_name"] == "Aarav Sharma"


def test_delete_appointment(client, appointment_payload):
    created = client.post("/api/appointments", json=appointment_payload).json()
    assert client.delete(f"/api/appointments/{created['id']}").status_code == 204
    assert client.get(f"/api/appointments/{created['id']}").status_code == 404


def test_stats(client, appointment_payload):
    client.post("/api/appointments", json=appointment_payload)
    client.post("/api/appointments", json={**appointment_payload, "status": "COMPLETED"})
    client.post("/api/appointments", json={**appointment_payload, "status": "CANCELLED"})
    assert client.get("/api/appointments/stats").json() == {
        "total": 3, "scheduled": 1, "checkedIn": 0, "completed": 1, "cancelled": 1,
    }
