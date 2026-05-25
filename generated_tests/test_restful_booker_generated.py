import pytest
from shared.tooling.api_tool import RestfulBookerClient


@pytest.fixture(scope="module")
def client():
    return RestfulBookerClient()


def test_health_check(client):
    # GET /ping should respond with 201
    response = client.get("/ping")
    assert response.status_code == 201


def test_booking_ids_list(client):
    # GET /booking should return list of booking ids
    response = client.get("/booking")
    assert response.status_code == 200
    booking_ids = response.json()
    assert isinstance(booking_ids, list)
    for item in booking_ids:
        assert "bookingid" in item
        assert isinstance(item["bookingid"], int)


def test_create_and_read_booking(client):
    # Create a booking with POST /booking
    booking_payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-06-01", "checkout": "2026-06-07"},
        "additionalneeds": "Lunch"
    }
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert "bookingid" in created and "booking" in created
    bookingid = created["bookingid"]
    assert created["booking"] == booking_payload

    # Read the booking back with GET /booking/{id}
    get_resp = client.get(f"/booking/{bookingid}")
    assert get_resp.status_code == 200
    fetched_booking = get_resp.json()
    assert fetched_booking == booking_payload

    # Cleanup - delete booking with auth token
    # Create auth token
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    assert auth_resp.status_code == 200
    token = auth_resp.json().get("token")
    assert isinstance(token, str)

    # Delete booking with auth token
    delete_resp = client.delete(f"/booking/{bookingid}", headers={"Cookie": f"token={token}"})
    assert delete_resp.status_code == 201


def test_create_patch_and_delete_booking_with_auth(client):
    # Create auth token first
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    assert auth_resp.status_code == 200
    token = auth_resp.json().get("token")
    assert isinstance(token, str)
    auth_headers = {"Cookie": f"token={token}"}

    # Create a booking
    booking_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "totalprice": 200,
        "depositpaid": False,
        "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-10"},
        "additionalneeds": "Dinner"
    }
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    bookingid = created["bookingid"]

    # Partially update booking with PATCH /booking/{id}
    patch_payload = {
        "firstname": "Alicia",
        "totalprice": 220,
        "depositpaid": True,
        "additionalneeds": "Breakfast"
    }
    patch_resp = client.patch(f"/booking/{bookingid}", json=patch_payload, headers=auth_headers)
    assert patch_resp.status_code == 200
    patched_booking = patch_resp.json()

    # Check patched fields were updated and others remain unchanged
    assert patched_booking["firstname"] == patch_payload["firstname"]
    assert patched_booking["totalprice"] == patch_payload["totalprice"]
    assert patched_booking["depositpaid"] == patch_payload["depositpaid"]
    assert patched_booking["additionalneeds"] == patch_payload["additionalneeds"]
    # Unchanged fields keep original value
    assert patched_booking["lastname"] == booking_payload["lastname"]
    assert patched_booking["bookingdates"] == booking_payload["bookingdates"]

    # Delete booking with auth
    delete_resp = client.delete(f"/booking/{bookingid}", headers=auth_headers)
    assert delete_resp.status_code == 201


def test_get_booking_not_found(client):
    # Expect 404 for a booking ID that doesn't exist
    non_existent_id = 99999999
    resp = client.get(f"/booking/{non_existent_id}")
    assert resp.status_code == 404


def test_update_booking_forbidden_without_auth(client):
    # Create a booking to attempt update without auth
    booking_payload = {
        "firstname": "NoAuth",
        "lastname": "User",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-06-01", "checkout": "2026-06-07"},
        "additionalneeds": "None"
    }
    create_resp = client.post("/booking", json=booking_payload)
    bookingid = create_resp.json()["bookingid"]

    # Attempt put without auth
    put_resp = client.put(f"/booking/{bookingid}", json=booking_payload)
    assert put_resp.status_code == 403

    # Cleanup with auth
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    token = auth_resp.json()["token"]
    client.delete(f"/booking/{bookingid}", headers={"Cookie": f"token={token}"})


def test_patch_booking_forbidden_without_auth(client):
    # Create booking for patch test
    booking_payload = {
        "firstname": "Patch",
        "lastname": "User",
        "totalprice": 150,
        "depositpaid": False,
        "bookingdates": {"checkin": "2026-06-01", "checkout": "2026-06-07"},
        "additionalneeds": "Spa"
    }
    create_resp = client.post("/booking", json=booking_payload)
    bookingid = create_resp.json()["bookingid"]

    # Attempt patch without auth
    patch_payload = {"firstname": "Hacker"}
    patch_resp = client.patch(f"/booking/{bookingid}", json=patch_payload)
    assert patch_resp.status_code == 403

    # Cleanup with auth
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    token = auth_resp.json()["token"]
    client.delete(f"/booking/{bookingid}", headers={"Cookie": f"token={token}"})
