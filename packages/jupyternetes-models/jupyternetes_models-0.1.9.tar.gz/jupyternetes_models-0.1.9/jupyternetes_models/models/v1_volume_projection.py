from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_cluster_trustbundle_projection import V1ClusterTrustBundleProjection
from .v1_config_map_projection import V1ConfigMapProjection
from .v1_downwardapi_projection import V1DownwardAPIProjection
from .v1_secret_projection import V1SecretProjection
from .v1_serviceaccounttoken_projection import V1ServiceAccountTokenProjection


class V1VolumeProjection(BaseModel):
    cluster_trust_bundle : Optional[V1ClusterTrustBundleProjection] = Field(default = None, alias = "clusterTrustBundle")
    config_map : Optional[V1ConfigMapProjection] = Field(default = None, alias = "configMap")
    downward_api : Optional[V1DownwardAPIProjection] = Field(default = None, alias = "downwardAPI")
    secret : Optional[V1SecretProjection] = Field(default = None, alias = "secret")
    service_account_token : Optional[V1ServiceAccountTokenProjection] = Field(default = None, alias = "serviceAccountToken")