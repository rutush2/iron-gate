import json
import os
import hashlib


class KeyVault:
    def __init__(self, storage_file="keys.json"):
        self.storage_file = storage_file
        self.mock_db = self._load_keys()

    def _load_keys(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                return json.load(f)
        return {}

    def _save_keys(self):
        with open(self.storage_file, "w") as f:
            json.dump(self.mock_db, f)

    def _hash_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    def generate_api_key(self, user_id: str) -> str:
        import os as core_os
        raw_key = f"iron_{core_os.urandom(16).hex()}"
        hashed_key = self._hash_key(raw_key)
        self.mock_db[hashed_key] = {"user_id": user_id}
        self._save_keys()
        return raw_key

    def verify_key(self, api_key: str) -> bool:
        hashed_key = self._hash_key(api_key)
        return hashed_key in self.mock_db