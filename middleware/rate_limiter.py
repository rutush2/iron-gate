import time
from fastapi import HTTPException, Request

class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.history = {}


    async def __call__(self, request: Request):
        if request.url.path in ["/status", "/admin/generate"]:
            return

        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return

        import hashlib
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()

        now = time.time()

        if hashed_key not in self.history:
            self.history[hashed_key] = []

        self.history[hashed_key] = [
            t for t in self.history[hashed_key]
            if now - t < self.window_seconds
        ]
        if len(self.history[hashed_key]) >= self.requests_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please slow down."
            )

        self.history[hashed_key].append(now)

