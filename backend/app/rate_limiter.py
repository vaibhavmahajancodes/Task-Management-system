"""
Shared slowapi Limiter instance. Defined in its own module (rather than in
main.py) so route modules can import and apply `@limiter.limit(...)`
decorators without causing a circular import with the FastAPI app.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
