from .mockers import JupyterMockers
from ..models import V1JupyterNotebookInstance
from pydantic import TypeAdapter

class TestV1JupyterNotebookInstance:
    adapter = TypeAdapter(V1JupyterNotebookInstance)
    def test_instance(self):
        mockers = JupyterMockers()
        instance = mockers.mock_instance()
        template = mockers.mock_instance_template()

        assert instance.metadata.name == "test"
        assert instance.spec.template.name == "test"

        pods = instance.GenerateV1PodDefinitions(template)

        assert len(pods) == 1

        assert pods[0].spec != None
        assert pods[0].spec.containers[0]["env"][1]["value"] == "test-user@someorg"
        
    def test_instance_as_json(self):
        mockers = JupyterMockers()
        instance = mockers.mock_instance()
        self.adapter.dump_json(instance, by_alias = True)
