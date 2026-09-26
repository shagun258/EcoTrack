def test_non_admin_cannot_create_recycling_center(client, auth_headers):
    resp = client.post("/api/recycling-centers", json={
        "name": "Test Center", "address": "x", "latitude": 1, "longitude": 1, "accepted_waste_types": ["Plastic"],
    }, headers=auth_headers)
    assert resp.status_code == 403


def test_non_admin_cannot_list_all_users(client, auth_headers):
    resp = client.get("/api/admin/users", headers=auth_headers)
    assert resp.status_code == 403


def test_public_can_list_recycling_centers_without_auth(client):
    resp = client.get("/api/recycling-centers")
    assert resp.status_code == 200
    assert resp.json() == []


def test_user_cannot_view_another_users_pickup(client):
    r1 = client.post("/api/auth/register", json={"full_name": "Owner", "email": "owner@example.com", "password": "password123"})
    owner_headers = {"Authorization": f"Bearer {r1.json()['access_token']}"}

    r2 = client.post("/api/auth/register", json={"full_name": "Intruder", "email": "intruder@example.com", "password": "password123"})
    intruder_headers = {"Authorization": f"Bearer {r2.json()['access_token']}"}

    pickup = client.post("/api/pickups", json={
        "waste_type": "Metal", "quantity_kg": 2.0, "address": "Somewhere",
        "latitude": 1.0, "longitude": 1.0, "preferred_date": "2026-11-01", "preferred_time": "09:00:00",
    }, headers=owner_headers)
    assert pickup.status_code == 201
    pickup_id = pickup.json()["id"]

    resp = client.get(f"/api/pickups/{pickup_id}", headers=intruder_headers)
    assert resp.status_code == 403
