from typing import Any


def update(
    TABLE: str, where: str, args: list[Any], set: dict[str, Any | None]
) -> tuple[str, list[Any]]:
    d = {name: value for name, value in set.items() if value is not None}
    query = f"UPDATE {TABLE} SET {', '.join(d)} WHERE {where}"
    return query, [*d.values(), *args]
