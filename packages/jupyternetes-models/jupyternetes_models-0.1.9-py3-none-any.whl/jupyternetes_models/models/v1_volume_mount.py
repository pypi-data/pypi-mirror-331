from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1VolumeMount(BaseModel):
    mount_path : str = Field(alias = "mountPath", default = None)
    mount_propagation : Optional[str] = Field(default = None, alias = "mountPropagation")
    name : str = Field(default = None, alias = "name")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    recursive_read_only : Optional[str] = Field(default = None, alias = "recursiveReadOnly")
    sub_path : Optional[str] = Field(default = None, alias = "subPath")
    sub_path_expr : Optional[str] = Field(default = None, alias = "subPathExpr")