import httpx
import time
from fastapi import HTTPException, Request
from fastapi.responses import Response
from utils.load_balancer import LoadBalancer


class ProxyEngine:

    def __init__(self):
        self.balancer = LoadBalancer()
        self.analytics = []
        self.server_health = {}

    async def forward(self, path: str, request: Request):
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )

        start_time = time.perf_counter()
        base_url = await self.balancer.get_server()

        clean_path = path.replace("%2F", "/").replace("%2f", "/")
        while clean_path.startswith("/"):
            clean_path = clean_path[1:]

        target_url = f"{base_url}/{clean_path}"

        headers = {}
        for k, v in request.headers.items():
            k_lower = k.lower()
            if k_lower in ["host", "connection", "accept-encoding", "content-length"] or k_lower.startswith("sec"):
                continue
            headers[k] = v

        headers["accept-encoding"] = "identity"

        try:
            body_content = await request.body()
            if not body_content and request.method in ["POST", "PUT", "PATCH"]:
                body_content = b"{}"
            elif not body_content:
                body_content = None

            async with httpx.AsyncClient() as client:
                res = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=request.query_params,
                    content=body_content,
                    timeout=10.0
                )

                response_headers = {}
                for k, v in res.headers.items():
                    if k.lower() in ["content-length", "transfer-encoding", "connection", "content-encoding"]:
                        continue
                    response_headers[k] = v

                duration = (time.perf_counter() - start_time) * 1000
                self.analytics.append(
                    {"status_code": res.status_code, "latency": duration}
                )

                return Response(
                    content=res.content,
                    status_code=res.status_code,
                    headers=response_headers,
                    media_type="application/json"
                )
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            self.analytics.append({"status_code": 502, "latency": duration})
            raise HTTPException(
                status_code=502, detail="Gateway error: Target unreachable"
            )