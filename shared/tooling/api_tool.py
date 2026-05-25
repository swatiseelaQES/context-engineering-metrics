from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

import requests
from requests import Response
from urllib3.exceptions import InsecureRequestWarning

from shared.config import Settings, get_settings


@dataclass
class RestfulBookerClient:
    settings: Settings

    @classmethod
    def from_env(cls) -> "RestfulBookerClient":
        return cls(get_settings())

    def __post_init__(self) -> None:
        if not self.settings.restful_booker_verify_ssl:
            warnings.simplefilter("ignore", InsecureRequestWarning)

    @property
    def base_url(self) -> str:
        return self.settings.restful_booker_base_url

    @property
    def verify_ssl(self) -> bool:
        return self.settings.restful_booker_verify_ssl

    def request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("verify", self.verify_ssl)
        kwargs.setdefault("timeout", 30)
        return requests.request(method, url, **kwargs)

    def ping(self) -> Response:
        return self.request("GET", "/ping")

    def get_booking_ids(self) -> Response:
        return self.request("GET", "/booking")

    def create_token(self) -> str:
        response = self.request(
            "POST",
            "/auth",
            json={
                "username": self.settings.restful_booker_username,
                "password": self.settings.restful_booker_password,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()["token"]

    def create_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.request(
            "POST", "/booking", json=payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    def get_booking(self, booking_id: int) -> Response:
        return self.request("GET", f"/booking/{booking_id}")

    def delete_booking(self, booking_id: int, token: str) -> Response:
        return self.request("DELETE", f"/booking/{booking_id}", headers={"Cookie": f"token={token}"})

    def patch_booking(self, booking_id: int, token: str, payload: dict[str, Any]) -> Response:
        return self.request(
            "PATCH",
            f"/booking/{booking_id}",
            json=payload,
            headers={"Content-Type": "application/json", "Cookie": f"token={token}"},
        )

def is_valid_status(actual_status: int, expected_status: int) -> bool:
        return actual_status == expected_status


