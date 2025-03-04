from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_jupyter_notebook_instance_template_spec import V1JupyterNotebookInstanceTemplateSpec
from .v1_objectmeta import V1ObjectMeta


class V1JupyterNotebookInstanceTemplate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)

    api_version : Optional[str] = Field(default = "jupyternetes.io/v1", alias = "apiVersion")
    kind : Optional[str] = Field(default = "JupyterNotebookInstanceTemplate", alias = "kind")
    metadata : Optional[SkipValidation[V1ObjectMeta]] = Field(default = None, alias = "metadata")
    spec : Optional[V1JupyterNotebookInstanceTemplateSpec] = Field(default = V1JupyterNotebookInstanceTemplateSpec(), alias = "spec")
