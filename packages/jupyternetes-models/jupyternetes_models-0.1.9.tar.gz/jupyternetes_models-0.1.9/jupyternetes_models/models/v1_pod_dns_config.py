from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_pod_dns_config_option import V1PodDNSConfigOption 


class V1PodDNSConfig(BaseModel):
    nameservers : Optional[list[str]] = Field(default = None, alias = "nameservers")
    options : Optional[list[V1PodDNSConfigOption]] = Field(default = None, alias = "options")
    searches : Optional[list[str]] = Field(default = None, alias = "searches")