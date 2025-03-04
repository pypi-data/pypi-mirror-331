from ..models import (
    V1JupyterNotebookInstanceTemplate, 
    V1JupyterNotebookInstanceTemplateSpec, 
    V1JupyterNotebookInstanceTemplateSpecPod, 
    V1PodSpec,
    V1JupyterNotebookInstance, 
    V1JupyterNotebookInstanceSpec, 
    V1JupyterNotebookInstanceSpecTemplate,
    V1Container, 
    V1EnvVar, 
    V1ObjectMeta
)


class JupyterMockers:
    def mock_instance(self, name : str = "test", namespace : str = "test", template_name : str = "test", template_namespace : str = "test", resource_version = "811600"):
        metadata = V1ObjectMeta(
            name = name,
            namespace = namespace,
            labels = {
                'jupyternetes.io/test-label': 'test'
            },
            annotations= {
                'jupyternetes.io/test-annotation': 'test'

            },
        )

        return V1JupyterNotebookInstance(
            metadata= metadata,
            spec = V1JupyterNotebookInstanceSpec(
                template = V1JupyterNotebookInstanceSpecTemplate(
                    name = template_name,
                    namespace = template_namespace
                ),
                variables = {
                    "username" : "test-user",
                    "unescaped-username" : "test-user"
                }
            )
        )

    def mock_instance_template(self, name : str = "test", namespace : str = "test-namespace", resource_version = "811601"):
        metadata = V1ObjectMeta(
            name = name,
            namespace = namespace,
            labels = {
                'jupyternetes.io/test-label': 'test'
            },
            annotations= {
                'jupyternetes.io/test-annotation': 'test'

            },
        )
        
        return V1JupyterNotebookInstanceTemplate(
            metadata= metadata,
            spec= V1JupyterNotebookInstanceTemplateSpec(
                pods = [
                    V1JupyterNotebookInstanceTemplateSpecPod(
                        name = name,
                        spec = V1PodSpec(
                            containers=[
                                V1Container(
                                    args = [
                                        "install",
                                        "--set-string",
                                        "global.systemDefaultRegistry="
                                    ],
                                    env = [
                                        V1EnvVar(
                                            name = "NAME",
                                            value = "test"
                                        ),
                                        V1EnvVar(
                                            name = "USER",
                                            value = "{username}@someorg"
                                        )
                                    ],
                                    image="test/test:0.1.0",
                                    name = "tester"
                                )
                            ]
                        ) 
                    )
                ]
            )
        )
