**Auto-generated** using [documatic](https://github.com/aspizu/documatic)


# lib


 - [Model](#Model)



## `db`


```py

def db():
    ...
```

## `time`


```py

def time() -> int:
    ...
```

## `successful_response`


```py

def successful_response(data: dict[str, JSON]):
    ...
```

## `failed_response`


```py

def failed_response(exception: str, data: dict[str, JSON]):
    ...
```

## `exception_response`


```py

def exception_response(exception: BaseException, data: dict[str, JSON]):
    ...
```

## `isoftype`


```py

def isoftype(obj: Any, T: Any) -> bool:
    ...
```

## `POST_endpoint_decorator`


```py

def POST_endpoint_decorator(app: "App", path: str, require_logged_in: bool):
    ...
```

## `GET_endpoint_decorator`


```py

def GET_endpoint_decorator(app: "App", path: str, require_logged_in: bool):
    ...
```

# `Model`


```py

class Model:
    ...
```

## `__init__`


```py

def __init__(self, data: dict[str, Any]):
    ...
```

## `to_dict`


```py

def to_dict(self):
    ...
```

## `__repr__`


```py

def __repr__(self):
    ...
```

## `__rich_repr__`


```py

def __rich_repr__(self) -> "RichReprResult":
    ...
```

