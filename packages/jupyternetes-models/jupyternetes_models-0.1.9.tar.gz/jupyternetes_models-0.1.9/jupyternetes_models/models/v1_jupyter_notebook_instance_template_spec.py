from pydantic import BaseModel, Field
from typing import Optional
from .v1_jupyter_notebook_instance_template_spec_pod import V1JupyterNotebookInstanceTemplateSpecPod


class V1JupyterNotebookInstanceTemplateSpec(BaseModel):
    pods : Optional[list[V1JupyterNotebookInstanceTemplateSpecPod]] = Field(default = [], alias = "pods")