import os

def verify_api_key(provided_key: str) -> bool:
    expected_key = os.getenv("API_KEY", "scamshield_2026_secure_key")
    return provided_key == expected_key
