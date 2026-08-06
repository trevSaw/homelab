"""KORA Runtime package.

The FastAPI application lives in ``app.main``. Keeping package import free of
application startup side effects lets transport/domain modules remain reusable.
"""
