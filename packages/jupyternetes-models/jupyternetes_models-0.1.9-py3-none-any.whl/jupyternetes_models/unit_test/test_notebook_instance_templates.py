from .mockers import JupyterMockers
from ..models import V1JupyterNotebookInstanceTemplate
from pydantic import TypeAdapter

class TestV1JupyterNotebookInstanceTemplate:
    adapter = TypeAdapter(V1JupyterNotebookInstanceTemplate)

    def test_template(self):
        mockers = JupyterMockers()
        template = mockers.mock_instance_template()

        assert template.metadata.name == "test"
        assert template.spec.pods[0].name == "test"
        assert template.spec.pods[0].spec.containers[0].name == "tester"
        
    def test_template_as_json(self):
        mockers = JupyterMockers()
        template = mockers.mock_instance_template()
        self.adapter.dump_json(template, by_alias = True)