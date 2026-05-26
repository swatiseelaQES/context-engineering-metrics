def baseline_restful_booker_tests() -> str:
    return '''
from shared.config import Settings
from shared.tooling.api_tool import RestfulBookerClient


def test_ping_health_check():
    client = RestfulBookerClient(Settings())
    response = client.get("/ping")
    assert response.status_code in (200, 201)
'''.strip()


def rag_restful_booker_tests() -> str:
    return baseline_restful_booker_tests() + '''


def test_get_booking_ids():
    client = RestfulBookerClient(Settings())
    response = client.get("/booking")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_booking_contract_shape():
    client = RestfulBookerClient(Settings())

    payload = {
        "firstname": "Rag",
        "lastname": "Generated",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-02",
        },
        "additionalneeds": "Breakfast",
    }

    response = client.post(
        "/booking",
        json=payload,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "bookingid" in body
    assert "booking" in body
'''.strip()


def memory_restful_booker_tests() -> str:
    return rag_restful_booker_tests() + '''


def test_created_booking_preserves_nested_bookingdates():
    client = RestfulBookerClient(Settings())

    payload = {
        "firstname": "Memory",
        "lastname": "Generated",
        "totalprice": 456,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2026-02-01",
            "checkout": "2026-02-05",
        },
        "additionalneeds": "Late checkout",
    }

    create_response = client.post(
        "/booking",
        json=payload,
        headers={"Content-Type": "application/json"},
    )

    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    read_response = client.get(f"/booking/{booking_id}")
    assert read_response.status_code == 200

    body = read_response.json()
    assert body["firstname"] == payload["firstname"]
    assert body["bookingdates"]["checkin"] == payload["bookingdates"]["checkin"]
    assert body["bookingdates"]["checkout"] == payload["bookingdates"]["checkout"]
'''.strip()


def tool_restful_booker_tests() -> str:
    return memory_restful_booker_tests() + '''


def test_auth_token_creation():
    client = RestfulBookerClient(Settings())

    response = client.post(
        "/auth",
        json={"username": "admin", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert "token" in response.json()


def test_patch_booking_with_auth_and_cleanup():
    client = RestfulBookerClient(Settings())

    payload = {
        "firstname": "Tool",
        "lastname": "Before",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-03-01",
            "checkout": "2026-03-02",
        },
        "additionalneeds": "Breakfast",
    }

    create_response = client.post(
        "/booking",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    auth_response = client.post(
        "/auth",
        json={"username": "admin", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )
    token = auth_response.json()["token"]

    patch_response = client.patch(
        f"/booking/{booking_id}",
        json={"firstname": "ToolUpdated"},
        headers={
            "Content-Type": "application/json",
            "Cookie": f"token={token}",
        },
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["firstname"] == "ToolUpdated"

    delete_response = client.delete(
        f"/booking/{booking_id}",
        headers={"Cookie": f"token={token}"},
    )

    assert delete_response.status_code in (200, 201)
'''.strip()


def orchestration_restful_booker_tests() -> str:
    return tool_restful_booker_tests() + '''


def test_get_missing_booking_returns_404():
    client = RestfulBookerClient(Settings())
    response = client.get("/booking/999999999")
    assert response.status_code == 404


def test_delete_without_auth_returns_forbidden():
    client = RestfulBookerClient(Settings())

    payload = {
        "firstname": "Orchestration",
        "lastname": "Negative",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-04-01",
            "checkout": "2026-04-02",
        },
        "additionalneeds": "Breakfast",
    }

    create_response = client.post(
        "/booking",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    delete_response = client.delete(f"/booking/{booking_id}")
    assert delete_response.status_code in (403, 405)

    auth_response = client.post(
        "/auth",
        json={"username": "admin", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )
    token = auth_response.json()["token"]

    client.delete(
        f"/booking/{booking_id}",
        headers={"Cookie": f"token={token}"},
    )
'''.strip()


def basic_restful_booker_tests() -> str:
    return baseline_restful_booker_tests()