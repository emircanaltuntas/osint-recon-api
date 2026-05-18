from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class IdentityData(BaseModel):
    username: Optional[str] = None
    found_accounts: List[str] = Field(default_factory=list, alias="foundAccounts")
    full_name: Optional[str] = Field(None, alias="fullName")

    model_config = ConfigDict(populate_by_name=True)

class BreachData(BaseModel):
    source: str
    year: Optional[int] = None

class ContactData(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password_breaches: List[BreachData] = Field(default_factory=list, alias="passwordBreaches")

    model_config = ConfigDict(populate_by_name=True)

class NetworkDNSInfo(BaseModel):
    geo: Optional[str] = None
    ip: Optional[str] = None

class NetworkData(BaseModel):
    query: Optional[str] = None
    status: Optional[str] = None
    continent: Optional[str] = None
    continentCode: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None
    regionName: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    zip: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = None
    offset: Optional[int] = None
    currency: Optional[str] = None
    isp: Optional[str] = None
    org: Optional[str] = None
    as_info: Optional[str] = Field(None, alias="as")
    asname: Optional[str] = None
    mobile: bool = False
    proxy: bool = False
    hosting: bool = False
    dns: Optional[NetworkDNSInfo] = None
    edns: Optional[NetworkDNSInfo] = None

    model_config = ConfigDict(populate_by_name=True)

class DNSRecord(BaseModel):
    type: str
    value: str
    ttl: Optional[int] = None

class DNSData(BaseModel):
    domain: str
    records: List[DNSRecord] = Field(default_factory=list)
    subdomains: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

class WhoisData(BaseModel):
    registrar: Optional[str] = None
    organization: Optional[str] = None
    creation_date: Optional[str] = Field(None, alias="creationDate")
    expiration_date: Optional[str] = Field(None, alias="expirationDate")
    last_updated: Optional[str] = Field(None, alias="lastUpdated")
    status: List[str] = Field(default_factory=list)
    name_servers: List[str] = Field(default_factory=list, alias="nameServers")

    model_config = ConfigDict(populate_by_name=True)

class AggregatedData(BaseModel):
    identity: Optional[IdentityData] = None
    contact: Optional[ContactData] = None
    network: Optional[NetworkData] = None
    dns: Optional[DNSData] = None
    whois: Optional[WhoisData] = None

class ResponseMetadata(BaseModel):
    execution_time_ms: float = Field(..., alias="executionTimeMs")
    cached: bool

    model_config = ConfigDict(populate_by_name=True)

class UnifiedResponse(BaseModel):
    status: str = "completed"
    data: AggregatedData
    metadata: ResponseMetadata
