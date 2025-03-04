from pytest import mark
from ..unit_test.mockers import JupyterMockers
from ..clients import JupyterNotebookInstanceTemplateClient
from logging import Logger
from kubernetes_asyncio.config import load_kube_config 
from kubernetes_asyncio.client import ApiClient, CustomObjectsApi, CoreV1Api
from kubernetes_asyncio.client.models import V1PodSpec, V1Pod, V1ObjectMeta

class TestJupyterNotebookInstanceTemplate:
    log = Logger("TestJupyterNotebookInstanceTemplate")
    
    async def connect(self) -> JupyterNotebookInstanceTemplateClient:
        await load_kube_config()
        api_client = ApiClient()
        client = JupyterNotebookInstanceTemplateClient(log = self.log);
        return client

        
    async def connect_with_core(self) -> (JupyterNotebookInstanceTemplateClient, CoreV1Api):
        await load_kube_config()
        api_client = ApiClient()
        core_api = CoreV1Api(api_client=api_client)
        k8s_api = CustomObjectsApi(api_client=api_client)
        client = JupyterNotebookInstanceTemplateClient(log = self.log);
        return client, core_api    
    
    @mark.asyncio
    async def test_read(self):
        client = await self.connect()
        item = await client.get("jupyternetes", "default-template")
        for pod in item.spec.pods:
            spec = pod.GetPodSpec({
                "username" : "test-user",
                "unescaped_username" : "test-user"
            })
            assert len(spec.containers) > 0
            assert spec.containers[0]["name"] == "notebook"
            assert spec.containers[0]["env"][0]["name"] == "JUPTERHUB_USERNAME"
            assert spec.containers[0]["env"][0]["value"] == "test-user"
