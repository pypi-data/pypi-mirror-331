from pytest import mark
from ..unit_test.mockers import JupyterMockers
from ..clients import JupyterNotebookInstanceClient, JupyterNotebookInstanceTemplateClient
from logging import Logger
from kubernetes_asyncio.config import load_kube_config 
from kubernetes_asyncio.client import ApiClient, CustomObjectsApi, CoreV1Api
from kubernetes_asyncio.client.models import V1PodSpec, V1Pod, V1ObjectMeta
from uuid import uuid4

class TestJupyterNotebookInstance:
    log = Logger("TestJupyterNotebookInstance")
    
    async def connect(self) -> (JupyterNotebookInstanceClient, JupyterNotebookInstanceTemplateClient, CoreV1Api):
        await load_kube_config()
        api_client = ApiClient()
        core_api = CoreV1Api(api_client=api_client)
        client = JupyterNotebookInstanceClient(log = self.log);
        template_client = JupyterNotebookInstanceTemplateClient(log = self.log);
        return client, template_client, core_api    
    
    @mark.asyncio
    async def test_read_and_write(self):
        client, template_client, core_api = await self.connect()

        #template = await template_client.get("jupyternetes", "default-template")
        mockers = JupyterMockers()
        namespace = "jupyternetes"
        template = mockers.mock_instance_template(namespace = namespace, name = str(uuid4()))
        instance = mockers.mock_instance(
            name = str(uuid4()), 
            namespace = namespace, 
            template_name = template.metadata.name, 
            template_namespace = template.metadata.namespace
            )

        created_template = await template_client.create_or_replace(
            namespace = namespace,
            name = template.metadata.name,
            body = template
            )

        created_instance = await client.create_or_replace(
            namespace = namespace,
            name = instance.metadata.name,
            body = instance
            )

        instance.metadata.labels["jupyternetes.io/test-version"] = "v2"
        updated_instance = await client.create_or_replace(
            namespace = namespace,
            name = instance.metadata.name,
            body = instance
            )

        await client.delete(namespace, instance.metadata.name)
        await template_client.delete(namespace, template.metadata.name)
