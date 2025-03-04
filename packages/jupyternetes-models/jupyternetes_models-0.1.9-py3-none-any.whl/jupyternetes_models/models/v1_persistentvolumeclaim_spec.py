from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_typed_localobjectreference import V1TypedLocalObjectReference
from .v1_typed_objectreference import V1TypedObjectReference
from .v1_volume_resourcerequirements import V1VolumeResourceRequirements
from .v1_label_selector import V1LabelSelector


class V1PersistentVolumeClaimSpec(BaseModel):
    access_modes : Optional[list[str]] = Field(default = None, alias = "accessModes")
    data_source : Optional[V1TypedLocalObjectReference] = Field(default = None, alias = "dataSource")
    data_source_ref : Optional[V1TypedObjectReference] = Field(default = None, alias = "dataSourceRef")
    resources : Optional[V1VolumeResourceRequirements] = Field(default = None, alias = "resources")
    selector : Optional[V1LabelSelector] = Field(default = None, alias = "selector")
    storage_class_name : Optional[str] = Field(default = None, alias = "storageClassName")
    volume_attributes_class_name : Optional[str] = Field(default = None, alias = "volumeAttributesClassName")
    volume_mode : Optional[str] = Field(default = None, alias = "volumeMode")
    volume_name : Optional[str] = Field(default = None, alias = "volumeName")