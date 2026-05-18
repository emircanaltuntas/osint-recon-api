import asyncio
import re
from typing import Optional, List
from app.api.models import WhoisData

TLD_SERVERS = {
    'com': 'whois.verisign-grs.com',
    'net': 'whois.verisign-grs.com',
    'org': 'whois.pir.org',
    'info': 'whois.afilias.net',
    'io': 'whois.nic.io',
    'co': 'whois.nic.co',
    'me': 'whois.nic.me',
    'us': 'whois.nic.us',
    'tr': 'whois.nic.tr',
    'uk': 'whois.nic.uk',
    'ca': 'whois.cira.ca',
    'au': 'whois.auda.org.au',
    'de': 'whois.denic.de'
}

QUERY_IANA = "whois.iana.org"

async def _query_whois_server(server: str, domain: str, timeout: int = 5) -> str:
    response = b""
    writer = None
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(server, 43), timeout=timeout)

        query = f"{domain}\r\n".encode()
        writer.write(query)
        await writer.drain()

        while True:
            try:
                chunk = await asyncio.wait_for(reader.read(4096), timeout=timeout)
                if not chunk:
                    break
                response += chunk
            except asyncio.TimeoutError:
                break

    except Exception:
        return ""
    finally:
        if writer:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass

    try:
        return response.decode('utf-8', errors='ignore')
    except:
        return ""

async def fetch_whois_data(domain: str) -> Optional[WhoisData]:
    parts = domain.split('.')
    if len(parts) < 2:
        return None
    tld = parts[-1]

    server = TLD_SERVERS.get(tld)

    if not server:
        iana_resp = await _query_whois_server(QUERY_IANA, tld)
        match = re.search(r"refer:\s*([a-zA-Z0-9\.-]+)", iana_resp, re.IGNORECASE)
        if match:
            server = match.group(1)
        else:
            match = re.search(r"whois:\s*([a-zA-Z0-9\.-]+)", iana_resp, re.IGNORECASE)
            if match:
                server = match.group(1)

    if not server:
        server = f"whois.nic.{tld}"

    raw_text = await _query_whois_server(server, domain)

    referral_match = re.search(r"(?:Registrar WHOIS Server|Whois Server):\s*([a-zA-Z0-9\.-]+)", raw_text, re.IGNORECASE)
    if referral_match:
        redirect_server = referral_match.group(1).strip()
        if redirect_server and redirect_server != server and "://" not in redirect_server and "." in redirect_server:
            new_text = await _query_whois_server(redirect_server, domain)
            if len(new_text) > 50 and "No match" not in new_text:
                raw_text = new_text

    def get_val(patterns, text):
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                return val
        return None

    registrar = get_val([
        r"Registrar:\s*(.+)",
        r"Sponsoring Registrar:\s*(.+)",
        r"Registrar Name:\s*(.+)"
    ], raw_text)

    organization = get_val([
        r"Registrant Organization:\s*(.+)",
        r"OrgName:\s*(.+)",
        r"Tech Organization:\s*(.+)"
    ], raw_text)

    creation_date = get_val([
        r"Creation Date:\s*(.+)",
        r"Created:\s*(.+)",
        r"Registration Time:\s*(.+)",
        r"Domain Name Commencement Date:\s*(.+)"
    ], raw_text)

    expiration_date = get_val([
        r"Registry Expiry Date:\s*(.+)",
        r"Expiration Date:\s*(.+)",
        r"Expires on\.+:\s*(.+)",
        r"Paid-Till:\s*(.+)"
    ], raw_text)

    last_updated = get_val([
        r"Updated Date:\s*(.+)",
        r"Last Updated:\s*(.+)",
        r"Changed:\s*(.+)"
    ], raw_text)

    ns = []
    ns_matches = re.findall(r"(?:Name Server|nserver):\s*([a-zA-Z0-9\.-]+)", raw_text, re.IGNORECASE)
    for n in ns_matches:
        n_clean = n.strip().lower()
        if n_clean and "." in n_clean and n_clean not in ns:
            ns.append(n_clean)

    status = []
    status_matches = re.findall(r"Domain Status:\s*([a-zA-Z0-9\s]+)", raw_text, re.IGNORECASE)
    for s in status_matches:
        s_clean = s.strip().split(' ')[0]
        if s_clean and s_clean not in status:
            status.append(s_clean)

    if not any([registrar, organization, creation_date, ns]):
        if len(raw_text) < 100:
            return None

    return WhoisData(
        registrar=registrar,
        organization=organization,
        creation_date=creation_date,
        expiration_date=expiration_date,
        last_updated=last_updated,
        status=status,
        name_servers=ns
    )
