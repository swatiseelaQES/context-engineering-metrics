import pytest
from shared.tooling.api_tool import RestfulBookerClient


@pytest.fixture(scope="module")
def client():
    return RestfulBookerClient()


def test_health_check(client):
    # GET /ping returns 201 Created
    response = client.get("/ping")
    assert response.status_code == 201


def test_get_booking_ids_returns_list(client):
    # GET /booking returns 200 and a list (possibly empty) of booking ids
    response = client.get("/booking")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Each item should be dict with key bookingid as int
    for item in data:
        assert isinstance(item, dict)
        assert "bookingid" in item
        assert isinstance(item["bookingid"], int)


def test_create_and_read_booking(client):
    # Prepare booking payload
    booking_payload = {
        "firstname": "Alice",
        "lastname": "Smith",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-06-01",
            "checkout": "2026-06-10"
        },
        "additionalneeds": "Breakfast"
    }
    # POST /booking to create
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    create_data = create_resp.json()
    assert "bookingid" in create_data
    assert isinstance(create_data["bookingid"], int)
    assert "booking" in create_data
    created_booking = create_data["booking"]
    for key in booking_payload:
        assert created_booking[key] == booking_payload[key]

    booking_id = create_data["bookingid"]

    # GET /booking/{id} to read
    get_resp = client.get(f"/booking/{booking_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    for key in booking_payload:
        assert get_data[key] == booking_payload[key]


def test_create_auth_token(client):
    auth_payload = {"username": "admin", "password": "password123"}
    response = client.post("/auth", json=auth_payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert isinstance(data["token"], str)
    # Return token for downstream tests
    return data["token"]


@pytest.fixture
def booking_with_auth_token(client):
    # Create booking to work with
    booking_payload = {
        "firstname": "Bob",
        "lastname": "Marley",
        "totalprice": 200,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-07-01",
            "checkout": "2026-07-15"
        },
        "additionalneeds": "Late Checkout"
    }
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    booking_id = create_resp.json()["bookingid"]

    # Create auth token
    auth_payload = {"username": "admin", "password": "password123"}
    auth_resp = client.post("/auth", json=auth_payload)
    assert auth_resp.status_code == 200
    token = auth_resp.json()["token"]

    # Set token for client authentication cookie header
    # The API requires token cookie named 'token' for auth operations
    auth_cookies = {"token": token}

    yield booking_id, auth_cookies

    # Cleanup - delete booking after test if still exists
    client.delete(f"/booking/{booking_id}", cookies=auth_cookies)


def test_patch_and_delete_booking_with_auth(client, booking_with_auth_token):
    booking_id, auth_cookies = booking_with_auth_token

    # PATCH /booking/{id} with auth token - partial update firstname and additionalneeds
    patch_payload = {
        "firstname": "Robert",
        "additionalneeds": "Dinner"
    }
    patch_resp = client.patch(f"/booking/{booking_id}", json=patch_payload, cookies=auth_cookies)
    assert patch_resp.status_code == 200
    patched_data = patch_resp.json()
    assert patched_data["firstname"] == patch_payload["firstname"]
    assert patched_data["additionalneeds"] == patch_payload["additionalneeds"]

    # GET booking to verify patch
    get_resp = client.get(f"/booking/{booking_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["firstname"] == patch_payload["firstname"]
    assert get_data["additionalneeds"] == patch_payload["additionalneeds"]

    # DELETE /booking/{id} with auth token
    delete_resp = client.delete(f"/booking/{booking_id}", cookies=auth_cookies)
    assert delete_resp.status_code == 201

    # GET booking after delete returns 404
    get_after_delete_resp = client.get(f"/booking/{booking_id}")
    assert get_after_delete_resp.status_code == 404


def test_negative_get_invalid_booking(client):
    # Get booking with non-existing id returns 404
    response = client.get("/booking/0")
    assert response.status_code == 404


def test_negative_patch_without_auth(client):
    # Create booking to test patch without auth
    booking_payload = {
        "firstname": "NoAuth",
        "lastname": "User",
        "totalprice": 100,
        "depositpaid": False,
        "bookingdates": {"checkin": "2026-08-01", "checkout": "2026-08-05"},
        "additionalneeds": None
    }
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    booking_id = create_resp.json()["bookingid"]

    # Attempt PATCH without auth cookie or basic auth
    patch_payload = {"firstname": "Hacker"}
    patch_resp = client.patch(f"/booking/{booking_id}", json=patch_payload)
    assert patch_resp.status_code == 403

    # Cleanup
    # Get auth token and delete booking
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    token = auth_resp.json()["token"]
    auth_cookies = {"token": token}
    delete_resp = client.delete(f"/booking/{booking_id}", cookies=auth_cookies)
    assert delete_resp.status_code == 201


def test_negative_delete_without_auth(client):
    # Create booking to test delete without auth
    booking_payload = {
        "firstname": "NoAuthDel",
        "lastname": "User",
        "totalprice": 120,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-09-01", "checkout": "2026-09-10"},
        "additionalneeds": ""
    }
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    booking_id = create_resp.json()["bookingid"]

    # Attempt DELETE without auth
    delete_resp = client.delete(f"/booking/{booking_id}")
    assert delete_resp.status_code == 403

    # Cleanup with auth
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    token = auth_resp.json()["token"]
    auth_cookies = {"token": token}
    delete_resp2 = client.delete(f"/booking/{booking_id}", cookies=auth_cookies)
    assert delete_resp2.status_code == 201
