from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_jupyter_notebook_instance import V1JupyterNotebookInstance
from kubernetes_asyncio.client.models import V1ListMeta


class V1JupyterNotebookInstanceList(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)

    api_version : Optional[str] = Field(default = "jupyternetes.io/v1", alias = "apiVersion")
    items : Optional[list[V1JupyterNotebookInstance]] = Field(default = [], alias = "items")
    kind : Optional[str] = Field(default = "JupyterNotebookInstanceList", alias = "kind")
    
    metadata : Optional[SkipValidation[V1ListMeta]] = Field(default = V1ListMeta(), alias = "metadata")