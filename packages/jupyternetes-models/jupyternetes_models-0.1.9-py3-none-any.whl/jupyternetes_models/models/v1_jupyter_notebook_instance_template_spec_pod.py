from pydantic import BaseModel, Field, SkipValidation, ConfigDict, TypeAdapter
from kubernetes_asyncio.client.models import V1PodSpec as NativeV1PodSpec
from .v1_pod_spec import V1PodSpec
from typing import Optional
import json


class V1JupyterNotebookInstanceTemplateSpecPod(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)

    name : Optional[str] = Field(default = "", alias = "name")
    annotations : Optional[dict[str, str]] = Field(default = {}, alias = "annotations")
    labels : Optional[dict[str, str]] = Field(default = {}, alias = "labels")
    spec: Optional[V1PodSpec] = Field(None, alias = "spec")

    def GetPodSpec(self, params : dict[str, str]) -> NativeV1PodSpec:
        type_adapter = TypeAdapter(V1PodSpec)
        dumped_json = type_adapter.dump_json(self.spec, exclude_none = True, serialize_as_any = True).decode("utf-8")
        
        for key in params.keys():
            dumped_json = dumped_json.replace(f"{{{key}}}", params[key])

        reformed_pod_spec = type_adapter.validate_json(dumped_json.encode("utf-8"))
        reformed_pod_spec_dict = type_adapter.dump_python(reformed_pod_spec)
        reformed_pod_spec_dict_filtered = {}
        for k in reformed_pod_spec_dict.keys(): 
            if k != "openapi_types" and k != "attribute_map":
                reformed_pod_spec_dict_filtered[k] = reformed_pod_spec_dict[k]

        return NativeV1PodSpec(**reformed_pod_spec_dict_filtered)