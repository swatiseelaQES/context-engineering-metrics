RESTFUL_BOOKER_PYTEST_TEMPLATE = '''from __future__ import annotations

from shared.tooling.api_tool import RestfulBookerClient


def sample_booking_payload(firstname: str = "Context", lastname: str = "Metrics") -> dict:
    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-06-01", "checkout": "2026-06-07"},
        "additionalneeds": "Breakfast",
    }


def test_ping_returns_created_status():
    client = RestfulBookerClient.from_env()
    response = client.ping()
    assert response.status_code == 201


def test_get_booking_ids_returns_a_list():
    client = RestfulBookerClient.from_env()
    response = client.get_booking_ids()
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_can_create_and_read_booking():
    client = RestfulBookerClient.from_env()
    payload = sample_booking_payload()

    created = client.create_booking(payload)
    booking_id = created["bookingid"]
    assert isinstance(booking_id, int)
    assert created["booking"]["firstname"] == payload["firstname"]

    fetched = client.get_booking(booking_id)
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["firstname"] == payload["firstname"]
    assert body["lastname"] == payload["lastname"]
    assert body["bookingdates"]["checkin"] == payload["bookingdates"]["checkin"]


def test_can_create_patch_and_delete_booking():
    client = RestfulBookerClient.from_env()
    token = client.create_token()
    created = client.create_booking(sample_booking_payload("Patch", "Candidate"))
    booking_id = created["bookingid"]

    patched = client.patch_booking(booking_id, token, {"firstname": "Updated"})
    assert patched.status_code == 200
    assert patched.json()["firstname"] == "Updated"

    deleted = client.delete_booking(booking_id, token)
    assert deleted.status_code == 201
    assert client.get_booking(booking_id).status_code == 404
'''
