import aiohttp
import asyncio
from typing import List, Optional
from app.api.models import DNSData, DNSRecord

DOH_URL = "https://dns.google/resolve"
CRT_SH_URL = "https://crt.sh/"

async def fetch_dns_records(domain: str) -> List[DNSRecord]:
    record_types = ["A", "AAAA", "MX", "NS", "TXT"]
    records = []

    async def query_doh(session, r_type):
        try:
            async with session.get(DOH_URL, params={"name": domain, "type": r_type}) as resp:
                if resp.status == 200:
                    return r_type, await resp.json()
        except Exception:
            pass
        return r_type, None

    async with aiohttp.ClientSession() as session:
        tasks = [query_doh(session, rt) for rt in record_types]
        results = await asyncio.gather(*tasks)

        for r_type, data in results:
            if not data:
                continue

            answers = data.get("Answer", [])
            for ans in answers:
                r_value = ans.get("data")
                r_ttl = ans.get("TTL")
                if r_value:
                    records.append(DNSRecord(
                        type=r_type,
                        value=r_value,
                        ttl=r_ttl
                    ))

    return records

async def fetch_subdomains_crtsh(domain: str) -> List[str]:
    params = {
        "q": f"%.{domain}",
        "output": "json"
    }

    subdomains = set()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CRT_SH_URL, params=params, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    for item in data:
                        name_value = item.get("name_value")
                        if name_value:
                            names = name_value.split("\n")
                            for name in names:
                                clean_name = name.strip().replace("*.", "")
                                if clean_name.endswith(domain) and clean_name != domain:
                                    subdomains.add(clean_name)
    except Exception:
        pass

    return list(subdomains)

async def fetch_dns_data(domain: str) -> Optional[DNSData]:
    task_records = fetch_dns_records(domain)
    task_subdomains = fetch_subdomains_crtsh(domain)

    results = await asyncio.gather(task_records, task_subdomains, return_exceptions=True)

    records = results[0] if isinstance(results[0], list) else []
    subdomains = results[1] if isinstance(results[1], list) else []

    return DNSData(
        domain=domain,
        records=records,
        subdomains=sorted(subdomains)
    )
