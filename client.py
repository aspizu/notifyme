from typing import Any

from requests import Session
from rich import print

API = "http://0.0.0.0:5000/api"
session = Session()


def post(endpoint: str, data: dict[str, Any] = {}) -> dict[str, Any]:
    return session.post(f"{API}/{endpoint}", json=data).json()


def get(endpoint: str, params: dict[str, Any] = {}) -> dict[str, Any]:
    return session.get(f"{API}/{endpoint}", params=params).json()


json = post("login", {"username": "npcguy", "password": "12345678"})
session.cookies["token"] = json["token"]

# json = post(
#    "new_post",
#    {
#        "content": "This is a post to showcase tags",
#        "recipients": [],
#        "tags": ["Tag 1", "Tag 2", "Tag 3", "FY-A"],
#    },
# )

json = post(
    "add_reaction",
    {
        "post_id": 3,
        "emoji": 1,
    },
)

print(json)
