from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_jupyter_notebook_instance_template import V1JupyterNotebookInstanceTemplate
from kubernetes_asyncio.client.models import V1ListMeta


class V1JupyterNotebookInstanceTemplateList(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)

    api_version : Optional[str] = Field(default = "jupyternetes.io/v1", alias = "apiVersion")
    items : Optional[list[V1JupyterNotebookInstanceTemplate]] = Field(default = [], alias = "items")
    kind : Optional[str] = Field(default = "JupyterNotebookInstanceTemplateList", alias = "kind")
    
    metadata : Optional[SkipValidation[V1ListMeta]] = Field(default = V1ListMeta(), alias = "metadata")