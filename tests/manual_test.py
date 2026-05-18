import asyncio
import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

async def run_verification():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Health Check
        print("Checking Health...")
        resp = await client.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
        print(f"Health OK: {resp.json()}")

        # 2. Search (Cache Miss)
        print("\nSearching (Expect Cache Miss)...")
        payload = {"query": "johndoe", "type": "username"}
        resp = await client.post(f"{BASE_URL}/api/v1/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        print(f"Status: {data['status']}")
        print(f"Execution Time: {data['metadata']['executionTimeMs']}ms")
        print(f"Cached: {data['metadata']['cached']}")
        
        if data['metadata']['cached'] is True:
            print("WARNING: Expected cached=False on first run.")

        # 3. Search (Cache Hit)
        print("\nSearching Again (Expect Cache Hit)...")
        resp = await client.post(f"{BASE_URL}/api/v1/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        print(f"Execution Time: {data['metadata']['executionTimeMs']}ms")
        print(f"Cached: {data['metadata']['cached']}")
        
        if data['metadata']['cached'] is False:
             print("WARNING: Expected cached=True on second run (Redis might not be running).")
        else:
            print("SUCCESS: Response was cached.")

if __name__ == "__main__":
    try:
        asyncio.run(run_verification())
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
