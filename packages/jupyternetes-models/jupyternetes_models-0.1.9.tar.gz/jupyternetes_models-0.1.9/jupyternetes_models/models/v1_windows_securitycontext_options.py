from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1WindowsSecurityContextOptions(BaseModel):
    gmsa_credential_spec : Optional[str] = Field(default = None, alias = "gmsaCredentialSpec")
    gmsa_credential_spec_name : Optional[str] = Field(default = None, alias = "gmsaCredentialSpecName")
    host_process : Optional[str] = Field(default = None, alias = "hostProcess")
    run_as_user_name : Optional[str] = Field(default = None, alias = "runAsUserName")