import asyncio
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.core.client import client
from app.services.cache import cache
from app.api.models import UnifiedResponse, AggregatedData, ResponseMetadata, IdentityData, ContactData, NetworkData
from app.services.normalize import normalizer
from app.services.scrapers.username import fetch_username_data

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    type: str

@router.post("/search", response_model=UnifiedResponse)
async def search_osint(request: SearchRequest):
    request.query = request.query.strip()

    start_time = time.time()
    cache_key = f"osint:v3:{request.type}:{request.query}"

    cached_data = await cache.get(cache_key)
    if cached_data:
        execution_time = (time.time() - start_time) * 1000
        return UnifiedResponse(
            status="completed",
            data=AggregatedData(**cached_data),
            metadata=ResponseMetadata(execution_time_ms=execution_time, cached=True)
        )

    from app.services.scrapers.ip import fetch_ip_data
    from app.services.scrapers.dns import fetch_dns_data
    from app.services.scrapers.whois import fetch_whois_data
    from app.services.scrapers.contact import fetch_email_breaches, fetch_phone_data

    async def dummy_task(): return None

    task_identity = dummy_task()
    task_contact = dummy_task()
    task_network = dummy_task()
    task_dns = dummy_task()
    task_whois = dummy_task()

    q_type = request.type.lower()

    if q_type == "ip":
        task_network = fetch_ip_data(request.query)
    elif q_type == "username":
        task_identity = fetch_username_data(request.query)
    elif q_type == "email":
        async def email_wrapper(query):
            breaches = await fetch_email_breaches(query)
            return {"email": query, "breaches": [{"name": b.source, "year": b.year} for b in breaches]}
        task_contact = email_wrapper(request.query)
    elif q_type == "phone":
        async def phone_wrapper(query):
            data = await fetch_phone_data(query)
            return {"phone": query, "carrier": data.get("carrier")}
        task_contact = phone_wrapper(request.query)
    elif q_type in ["domain", "dns", "whois"]:
        if q_type in ["domain", "dns"]:
            task_dns = fetch_dns_data(request.query)
        if q_type in ["domain", "whois"]:
            task_whois = fetch_whois_data(request.query)

    results = await asyncio.gather(
        task_identity,
        task_contact,
        task_network,
        task_dns,
        task_whois,
        return_exceptions=True
    )

    identity_raw, contact_raw, network_raw, dns_raw, whois_raw = results

    identity_model = None
    if isinstance(identity_raw, dict):
        identity_model = normalizer.normalize_identity(identity_raw)

    contact_model = None
    if isinstance(contact_raw, dict):
        contact_model = normalizer.normalize_contact(contact_raw)

    network_model = None
    if isinstance(network_raw, dict):
        network_model = normalizer.normalize_network(network_raw)

    dns_model = None
    if isinstance(dns_raw, Exception):
        pass
    elif dns_raw:
        dns_model = dns_raw

    whois_model = None
    if isinstance(whois_raw, Exception):
        pass
    elif whois_raw:
        whois_model = whois_raw

    aggregated = AggregatedData(
        identity=identity_model,
        contact=contact_model,
        network=network_model,
        dns=dns_model,
        whois=whois_model
    )

    await cache.set(cache_key, aggregated.model_dump(mode='json', by_alias=True))

    execution_time = (time.time() - start_time) * 1000

    return UnifiedResponse(
        status="completed",
        data=aggregated,
        metadata=ResponseMetadata(execution_time_ms=execution_time, cached=False)
    )
