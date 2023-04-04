from typing import Any

from requests import Session
from rich import print

API = "http://0.0.0.0:8000/api"
session = Session()


def post(endpoint: str, data: dict[str, Any] = {}) -> dict[str, Any]:
    return session.post(f"{API}/{endpoint}", json=data).json()


def get(endpoint: str, params: dict[str, Any] = {}) -> dict[str, Any]:
    return session.get(f"{API}/{endpoint}", params=params).json()


json = post("login", {"username": "aspizu", "password": "br000tal"})
session.cookies["token"] = json["token"]

print(
    get(
        "get_posts",
    )
)
