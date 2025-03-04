from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_label_selector import V1LabelSelector

class V1ClusterTrustBundleProjection(BaseModel):
    label_selector : Optional[V1LabelSelector] = Field(alias = "labelSelector", default = None)
    name : Optional[str] = Field(alias = "name", default = None)
    optional : Optional[bool] = Field(alias = "optional", default = None)
    path : str = Field(alias = "path", default = None)
    signer_name : Optional[str] = Field(alias = "signerName", default = None)