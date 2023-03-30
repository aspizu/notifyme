**Auto-generated** using [documatic](https://github.com/aspizu/documatic)


# session


 - [Session](#Session)

 - [Sessions](#Sessions)



## `is_username_valid`


```py

def is_username_valid(username: str) -> bool:
    ...
```

## `is_password_valid`


```py

def is_password_valid(password: str) -> bool:
    ...
```

## `hash_password`


```py

def hash_password(password: str, username: str) -> str:
    ...
```

# `Session`


```py

class Session:
    ...
```

# `Sessions`


```py

class Sessions:
    ...
```

## `__init__`


```py

def __init__(self) -> None:
    ...
```

## `get`


```py

def get(self, request: Request) -> Session | None:
    ...
```

## `new`


```py

def new(self, username: str) -> Session:
    ...
```

## `remove`


```py

def remove(self, session_or_token: Session | str) -> None:
    ...
```

