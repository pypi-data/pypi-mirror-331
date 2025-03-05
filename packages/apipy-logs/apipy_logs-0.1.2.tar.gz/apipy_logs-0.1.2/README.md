# apipy_logs

![Version](https://img.shields.io/badge/version-0.1.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.8%2B-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.38%2B-red.svg)
![MPL-2.0 license](https://img.shields.io/badge/license-MPL--2.0-cyan.svg)

apipy_logs is a python module to create, read and delete your logs

## How i can use it ?

### Importation

```python
from fastapi_logs.log_manager import LogManager, log_manager
```

### Type of log

```python
LogManager.DEBUG      # Represents a debug message
LogManager.INFO       # Represents an information message
LogManager.WARNING    # Represents a warning message
LogManager.ERROR      # Represents an error message
LogManager.CRITICAL   # Represents a critical message
```

### Methods

```python
log_manager.create_log(level: str, module: str, request: Request, log: str)  # Used to create a log
log_manager.clear_logs()                                                     # Used to to clear the logs
log_manager.get_logs() -> list[str]:                                         # Used to to to get the today logs
```


### Example

```python
from fastapi_logs.log_manager import LogManager, log_manager

@router.get("/create-log")
async def example(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    This endpoint is an example.
    """
    log_manager.create_log(
        LogManager.INFO,
        __file__,
        request,
        f"This is an example"
    )
    return {}
```
