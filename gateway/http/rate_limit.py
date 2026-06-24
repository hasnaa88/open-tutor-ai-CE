"""Shared rate limiter for brute-forceable endpoints (login, signup, invite
redemption, session join). Kept in its own module so routers can import it
without creating a circular import with the app factory.
"""


from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
