from ..models import (
    V1JupyterNotebookInstanceTemplate,
    V1JupyterNotebookInstanceTemplateList
)
from kubernetes_asyncio.client import CustomObjectsApi
from kubernetes_asyncio.client.exceptions import ApiException
from logging import Logger
from .kubernetes_client import KubernetesNamespacedCustomClient

class JupyterNotebookInstanceTemplateClient(KubernetesNamespacedCustomClient):
    def __init__(self, log: Logger):
        super().__init__(
            log = log, 
            group = "jupyternetes.io", 
            version = "v1", 
            plural = "jupyternotebookinstancetemplates", 
            kind = "JupyterNotebookInstanceTemplate",
            list_type = V1JupyterNotebookInstanceTemplateList,
            singleton_type = V1JupyterNotebookInstanceTemplate
            )