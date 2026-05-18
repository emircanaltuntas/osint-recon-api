from typing import Dict, Any, List
from app.api.models import IdentityData, ContactData, NetworkData, BreachData

class Normalizer:
    @staticmethod
    def normalize_identity(data: Any) -> IdentityData:
        username = None
        full_name = None
        found_accounts = []

        if isinstance(data, dict):
            username = data.get("username") or data.get("user") or data.get("query")
            full_name = data.get("full_name") or data.get("name")

            if "profiles" in data:
                found_accounts = [p.get("site") for p in data["profiles"] if isinstance(p, dict) and p.get("site")]
            elif "sites" in data:
                found_accounts = [s if isinstance(s, str) else s.get("name") for s in data["sites"]]
            elif "found_accounts" in data:
                found_accounts = data["found_accounts"]

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    site = item.get("site") or item.get("name")
                    if site:
                        found_accounts.append(site)

        return IdentityData(
            username=username,
            foundAccounts=found_accounts,
            fullName=full_name
        )

    @staticmethod
    def normalize_contact(data: Dict[str, Any]) -> ContactData:
        email = data.get("email")
        phone = data.get("phone")

        breaches = []
        if "breaches" in data:
            for b in data["breaches"]:
                breaches.append(BreachData(source=b.get("name"), year=b.get("year")))

        return ContactData(
            email=email,
            phone=phone,
            passwordBreaches=breaches
        )

    @staticmethod
    def normalize_network(data: Dict[str, Any]) -> NetworkData:
        return NetworkData(
            query=data.get("query"),
            status=data.get("status"),
            continent=data.get("continent"),
            continentCode=data.get("continentCode"),
            country=data.get("country"),
            countryCode=data.get("countryCode"),
            region=data.get("region"),
            regionName=data.get("regionName"),
            city=data.get("city"),
            district=data.get("district"),
            zip=data.get("zip"),
            lat=data.get("lat"),
            lon=data.get("lon"),
            timezone=data.get("timezone"),
            offset=data.get("offset"),
            currency=data.get("currency"),
            isp=data.get("isp"),
            org=data.get("org"),
            as_info=data.get("as"),
            asname=data.get("asname"),
            mobile=data.get("mobile", False),
            proxy=data.get("proxy", False),
            hosting=data.get("hosting", False),
            dns=data.get("dns"),
            edns=data.get("edns")
        )

normalizer = Normalizer()
