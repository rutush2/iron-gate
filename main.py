from fastapi import FastAPI, Depends, Request
from contextlib import asynccontextmanager
import asyncio
import httpx
from storage.key_vault import KeyVault
from middleware.auth_guard import AuthGuard
from middleware.rate_limiter import RateLimiter
from router.proxy_engine import ProxyEngine
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

vault = KeyVault()
guard = AuthGuard(vault)
limiter = RateLimiter(requests_limit=100, window_seconds=60)
proxy = ProxyEngine()

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def background_health_checker():
    while True:
        for server in proxy.balancer.servers:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(server, timeout=3.0)
                    if response.status_code < 400:
                        proxy.server_health[server] = "HEALTHY"
                    else:
                        proxy.server_health[server] = "UNHEALTHY"
            except Exception:
                proxy.server_health[server] = "CRITICAL (DOWN)"
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    checker_task = asyncio.create_task(background_health_checker())
    yield
    checker_task.cancel()


app = FastAPI(title="Iron Gate API Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status", tags=["System Configuration"])
async def status():
    return {"status": "Gateway Operational", "healthy_backends": proxy.server_health}


@app.post("/admin/generate", tags=["System Configuration"])
async def generate_key(user_id: str):
    new_key = vault.generate_api_key(user_id)
    return {"user_id": user_id, "api_key": new_key}


@app.get("/admin/metrics", tags=["System Configuration"])
async def get_metrics():
    traffic_usage = {}
    for hashed_key, record in vault.mock_db.items():
        timestamps = limiter.history.get(hashed_key, [])
        user_id = record.get("user_id", "Unknown")
        display_label = f"{user_id} ({hashed_key[:6]}...)"
        traffic_usage[display_label] = len(timestamps)

    recent_analytics = proxy.analytics[-50:]
    return {
        "status": "Engine Connected",
        "keys_in_vault": len(vault.mock_db),
        "active_keys": len([k for k, t in limiter.history.items() if t]),
        "target_servers": proxy.balancer.servers,
        "rate_limit_usage": traffic_usage,
        "performance_logs": recent_analytics,
        "upstream_health": proxy.server_health,
    }


@app.get("/proxy/{path:path}", tags=["Flexible Input Testing Mode"], operation_id="gateway_get_route")
async def custom_echo_get_route(path: str, request: Request):
    clean_path = path.strip("/")
    proxy.analytics.append({"status_code": 200, "latency": 5.0})
    return {
        "gateway_status": "Success",
        "requested_method": "GET",
        "typed_path": clean_path,
        "input_payload_received": None,
        "message": f"Successfully processed GET input for {clean_path or 'root proxy'}"
    }


@app.post("/proxy/{path:path}", tags=["Flexible Input Testing Mode"], operation_id="gateway_post_route")
async def custom_echo_post_route(path: str, request: Request):
    clean_path = path.strip("/")
    body_data = None
    try:
        body_data = await request.json()
    except Exception:
        raw_body = await request.body()
        if raw_body:
            body_data = raw_body.decode(errors="ignore")
    proxy.analytics.append({"status_code": 200, "latency": 5.0})
    return {
        "gateway_status": "Success",
        "requested_method": "POST",
        "typed_path": clean_path,
        "input_payload_received": body_data,
        "message": f"Successfully processed POST input for {clean_path or 'root proxy'}"
    }


@app.put("/proxy/{path:path}", tags=["Flexible Input Testing Mode"], operation_id="gateway_put_route")
async def custom_echo_put_route(path: str, request: Request):
    clean_path = path.strip("/")
    body_data = None
    try:
        body_data = await request.json()
    except Exception:
        raw_body = await request.body()
        if raw_body:
            body_data = raw_body.decode(errors="ignore")
    proxy.analytics.append({"status_code": 200, "latency": 5.0})
    return {
        "gateway_status": "Success",
        "requested_method": "PUT",
        "typed_path": clean_path,
        "input_payload_received": body_data,
        "message": f"Successfully processed PUT input for {clean_path or 'root proxy'}"
    }


@app.delete("/proxy/{path:path}", tags=["Flexible Input Testing Mode"], operation_id="gateway_delete_route")
async def custom_echo_delete_route(path: str, request: Request):
    clean_path = path.strip("/")
    proxy.analytics.append({"status_code": 200, "latency": 5.0})
    return {
        "gateway_status": "Success",
        "requested_method": "DELETE",
        "typed_path": clean_path,
        "input_payload_received": None,
        "message": f"Successfully processed DELETE input for {clean_path or 'root proxy'}"
    }


@app.patch("/proxy/{path:path}", tags=["Flexible Input Testing Mode"], operation_id="gateway_patch_route")
async def custom_echo_patch_route(path: str, request: Request):
    clean_path = path.strip("/")
    body_data = None
    try:
        body_data = await request.json()
    except Exception:
        raw_body = await request.body()
        if raw_body:
            body_data = raw_body.decode(errors="ignore")
    proxy.analytics.append({"status_code": 200, "latency": 5.0})
    return {
        "gateway_status": "Success",
        "requested_method": "PATCH",
        "typed_path": clean_path,
        "input_payload_received": body_data,
        "message": f"Successfully processed PATCH input for {clean_path or 'root proxy'}"
    }