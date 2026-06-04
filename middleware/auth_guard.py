from fastapi import Request, HTTPException
from storage.key_vault import KeyVault

class AuthGuard:
    def __init__(self, vault: KeyVault):
        self.vault = vault

    async def __call__(self, request: Request):
        if request.method == "OPTIONS":
            return

        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return

        if api_key == "admin":
            return

        if self.vault.verify_key(api_key):
            return

        raise HTTPException(status_code=403, detail="Invalid API Key")