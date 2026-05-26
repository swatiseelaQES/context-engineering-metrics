import pytest

from shared.config import Settings
from shared.tooling.api_tool import RestfulBookerClient


@pytest.fixture(scope="module")
def client():
    # SSL verification controlled by environment variables inside RestfulBookerClient
    return RestfulBookerClient(Settings())


def sample_booking_data():
    return {
        "firstname": "TestFirst",
        "lastname": "TestLast",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-12-01",
            "checkout": "2024-12-10"
        },
        "additionalneeds": "Breakfast"
    }


def sample_booking_patch_data():
    return {
        "firstname": "PatchedFirst",
        "lastname": "PatchedLast",
        "totalprice": 456,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2025-01-01",
            "checkout": "2025-01-05"
        },
        "additionalneeds": "Lunch"
    }


def test_ping_health_check(client):
    response = client.get("/ping")
    # Per contract, 201 response means reachable
    assert response.status_code == 201


def test_get_booking_ids(client):
    response = client.get("/booking")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "bookingid" in item
        assert isinstance(item["bookingid"], int)


def test_create_and_read_booking(client):
    # Create a booking
    booking_payload = sample_booking_data()
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    create_data = create_resp.json()
    assert "bookingid" in create_data
    assert "booking" in create_data
    booking_id = create_data["bookingid"]

    # Read back created booking
    get_resp = client.get(f"/booking/{booking_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()

    # Confirm returned booking data matches what was created
    for key in booking_payload:
        assert key in get_data
        if key == "bookingdates":
            assert booking_payload[key]["checkin"] == get_data[key]["checkin"]
            assert booking_payload[key]["checkout"] == get_data[key]["checkout"]
        else:
            assert booking_payload[key] == get_data[key]


@pytest.fixture
def auth_token(client):
    # Create token for admin user with known credentials per contract example
    auth_payload = {"username": "admin", "password": "password123"}
    response = client.post("/auth", json=auth_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "token" in json_data
    return json_data["token"]


def test_create_patch_and_delete_booking_with_auth(client, auth_token):
    booking_payload = sample_booking_data()

    # Create booking first
    create_resp = client.post("/booking", json=booking_payload)
    assert create_resp.status_code == 200
    booking_id = create_resp.json()["bookingid"]

    # Partially update booking with PATCH using token in cookie header
    patch_payload = sample_booking_patch_data()
    headers = {"Cookie": f"token={auth_token}"}
    patch_resp = client.patch(f"/booking/{booking_id}", json=patch_payload, headers=headers)
    assert patch_resp.status_code == 200
    patched_data = patch_resp.json()

    # Confirm patched fields updated correctly
    for key in patch_payload:
        if key == "bookingdates":
            assert patch_payload[key]["checkin"] == patched_data[key]["checkin"]
            assert patch_payload[key]["checkout"] == patched_data[key]["checkout"]
        else:
            assert patch_payload[key] == patched_data[key]

    # Delete booking with auth token
    delete_resp = client.delete(f"/booking/{booking_id}", headers=headers)
    assert delete_resp.status_code == 201

    # Confirm deleted booking no longer exists
    get_resp = client.get(f"/booking/{booking_id}")
    assert get_resp.status_code == 404


def test_partial_update_requires_auth(client):
    # Prepare booking and create
    booking_payload = sample_booking_data()
    create_resp = client.post("/booking", json=booking_payload)
    booking_id = create_resp.json()["bookingid"]

    patch_payload = {"firstname": "UnauthorizedPatch"}

    # Try to patch without auth token - expect 403 Forbidden
    patch_resp = client.patch(f"/booking/{booking_id}", json=patch_payload)
    assert patch_resp.status_code == 403

    # Cleanup with auth
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    token = auth_resp.json()["token"]
    headers = {"Cookie": f"token={token}"}
    client.delete(f"/booking/{booking_id}", headers=headers)


def test_delete_requires_auth(client):
    # Create booking
    booking_payload = sample_booking_data()
    create_resp = client.post("/booking", json=booking_payload)
    booking_id = create_resp.json()["bookingid"]

    # Attempt to delete without auth
    del_resp = client.delete(f"/booking/{booking_id}")
    assert del_resp.status_code == 403

    # Cleanup with auth
    auth_resp = client.post("/auth", json={"username": "admin", "password": "password123"})
    token = auth_resp.json()["token"]
    headers = {"Cookie": f"token={token}"}
    del_cleanup_resp = client.delete(f"/booking/{booking_id}", headers=headers)
    assert del_cleanup_resp.status_code == 201


def test_get_booking_not_found(client):
    # Use a very large booking ID unlikely to exist
    non_existent_id = 999999999
    resp = client.get(f"/booking/{non_existent_id}")
    assert resp.status_code == 404


def test_auth_token_creation_with_invalid_credentials(client):
    invalid_payload = {"username": "wrong", "password": "wrongpass"}
    resp = client.post("/auth", json=invalid_payload)
    # The contract does not specify exact response for invalid credentials,
    # but the real API returns 200 with no token, so check that token missing
    if resp.status_code == 200:
        assert "token" not in resp.json()
    else:
        # Alternative stable check below if server returns other code
        assert resp.status_code in (200, 403, 401)
