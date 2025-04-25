"""Context management for logging."""

import threading
import uuid
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Generator, Optional, TypeVar, cast

T = TypeVar('T')

# Thread-local storage for context information
_thread_local = threading.local()


def _get_context() -> Dict[str, Any]:
    """Get the current context data from thread-local storage."""
    if not hasattr(_thread_local, "context"):
        _thread_local.context = {}
    return cast(Dict[str, Any], _thread_local.context)


def _generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


@contextmanager
def log_context(**kwargs: Any) -> Generator[None, None, None]:
    """
    Context manager for adding context to logs.
    
    Example:
        with log_context(user_id="123", action="login"):
            logger.info("User logged in")
    """
    old_context = _get_context().copy()
    _thread_local.context = {**old_context, **kwargs}
    try:
        yield
    finally:
        _thread_local.context = old_context


def with_log_context(**context_kwargs: Any) -> Callable[
    [Callable[..., T]], Callable[..., T]
]:
    """
    Decorator to add context to logs in a function.
    
    Example:
        @with_log_context(component="authentication")
        def authenticate_user(username, password):
            logger.info(f"Authenticating user {username}")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with log_context(**context_kwargs):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def init_request_context(request_id: Optional[str] = None, **kwargs: Any) -> str:
    """
    Initialize a new request context with an optional request ID.
    
    Parameters
    ----------
    request_id : str, optional
        Request ID to use, or generate a new one if not provided
    **kwargs : Any
        Additional context to include in the log
    
    Returns
    -------
    str
        The request ID
    """
    request_id = request_id or _generate_request_id()
    context = {"request_id": request_id, "timestamp": datetime.now().isoformat()}
    context.update(kwargs)
    _thread_local.context = context
    return request_id


def clear_request_context() -> None:
    """Clear the request context for the current thread."""
    if hasattr(_thread_local, "context"):
        delattr(_thread_local, "context") 