from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from kubernetes_asyncio.client.models import V1Pod
from .v1_objectmeta import V1ObjectMeta
from .v1_jupyter_notebook_instance_spec import V1JupyterNotebookInstanceSpec
from .v1_jupyter_notebook_instance_template import V1JupyterNotebookInstanceTemplate


class V1JupyterNotebookInstance(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)

    api_version : Optional[str] = Field(default = "jupyternetes.io/v1", alias = "apiVersion")
    kind : Optional[str] = Field(default = "JupyterNotebookInstance", alias = "kind")
    metadata : Optional[V1ObjectMeta] = Field(default = None, alias = "metadata")
    spec : Optional[V1JupyterNotebookInstanceSpec] = Field(default = V1JupyterNotebookInstanceSpec(), alias = "spec")

    def UpdateStringUsingVariables(self, value : str):
        for key in self.spec.variables.keys():
            value = value.replace(f"{{{key}}}", self.spec.variables[key])
        return value

    def GenerateV1PodDefinitions(self, template : V1JupyterNotebookInstanceTemplate):
        pods : list[V1Pod] = []
        if self.spec.template.name != template.metadata.name:
            raise Exception(f"Template name on instance ({self.spec.template.name}) does not match specified template {template.metadata.name}")

        for pod in template.spec.pods:
            name : str = self.UpdateStringUsingVariables(pod.name)
            annotations = pod.annotations.copy()
            labels = pod.labels.copy()

            for key in annotations.keys():
                annotations[key] = self.UpdateStringUsingVariables(annotations[key])
            
            for key in labels.keys():
                labels[key] = self.UpdateStringUsingVariables(labels[key])

            pod_spec = pod.GetPodSpec(self.spec.variables)

            pod = V1Pod(
                metadata = V1ObjectMeta(
                    name = name,
                    annotations = annotations,
                    labels = labels
                ),
                spec = pod_spec
            )

            pods.append(pod)
        
        return pods
