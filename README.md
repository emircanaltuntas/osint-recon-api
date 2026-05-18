# OSINT Recon API

A high-performance OSINT data aggregator API that concurrently queries multiple intelligence sources, normalizes the data, and caches results using Redis.

## Features

- Concurrent execution with asyncio.gather for parallel API queries
- Fail-safe design where individual API failures do not block the entire request
- Redis caching with configurable TTL (default 1 hour)
- Unified JSON output using Pydantic v2
- Retry logic with exponential backoff
- Raw TCP WHOIS lookups (port 43) with referral following

## Supported Query Types

| Type | Source | Description |
|------|--------|-------------|
| username | Maigret (top 150 sites) | Checks username existence across social platforms |
| ip | ip-api.com | IP geolocation and network metadata |
| email | BreachDirectory (RapidAPI) | Email breach/leak detection |
| phone | Numverify | Phone number validation and carrier lookup |
| domain | Google DoH + crt.sh | DNS records and subdomain enumeration |
| whois | Raw WHOIS (TCP/43) | Domain registration information |

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **HTTP Client**: aiohttp with connection pooling
- **Validation**: Pydantic v2
- **Cache**: Redis (async)
- **Username OSINT**: Maigret library

## Setup

1. Clone the repository:

```bash
git clone https://github.com/emircanaltuntas/osint-recon-api.git
cd osint-recon-api
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables by copying the example file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```
RAPIDAPI_KEY=your_rapidapi_key
NUMVERIFY_API_KEY=your_numverify_key
REDIS_URL=redis://localhost:6379/0
```

4. Start Redis (required for caching):

```bash
redis-server
```

5. Run the server:

```bash
uvicorn app.main:app --reload
```

## API Usage

### Health Check

```
GET /health
```

### Search

```
POST /api/v1/search
Content-Type: application/json

{
  "query": "example_username",
  "type": "username"
}
```

### Example Response

```json
{
  "status": "completed",
  "data": {
    "identity": {
      "username": "example_username",
      "foundAccounts": ["GitHub", "Twitter", "Instagram"],
      "fullName": null
    },
    "contact": null,
    "network": null,
    "dns": null,
    "whois": null
  },
  "metadata": {
    "executionTimeMs": 4523.12,
    "cached": false
  }
}
```

## Project Structure

```
app/
├── main.py
├── core/
│   ├── config.py
│   └── client.py
├── api/
│   ├── endpoints.py
│   └── models.py
└── services/
    ├── cache.py
    ├── normalize.py
    ├── identity.py
    └── scrapers/
        ├── username.py
        ├── ip.py
        ├── dns.py
        ├── whois.py
        └── contact.py
```

## License

MIT
