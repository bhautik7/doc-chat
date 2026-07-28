from contextlib import contextmanager
from typing import Iterator, Type

from fastapi import HTTPException


@contextmanager
def http_error_on(exception_type: Type[Exception], status_code: int) -> Iterator[None]:
    """Translate a domain exception raised in the block into an HTTPException."""
    try:
        yield
    except exception_type as exc:
        raise HTTPException(status_code=status_code, detail=str(exc))
