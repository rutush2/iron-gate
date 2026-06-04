import httpx
import asyncio


class LoadBalancer:
    def __init__(self):
        self.servers = [
            "https://jsonplaceholder.typicode.com",
        ]
        self.current_index = 0

    async def is_server_alive(self, url: str) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=2.0)
                return response.status_code == 200
            except Exception:
                return False


    async def get_server(self) -> str:
        for _ in range(len(self.servers)):
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)

            if await self.is_server_alive(server):
                return server

        return self.servers[0]

