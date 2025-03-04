from .mockers import JupyterMockers

class TestV1JupyterNotebookInstanceTemplate:
    def test_pods(self):
        mockers = JupyterMockers()
        template = mockers.mock_instance_template()
        instance = mockers.mock_instance()
        
