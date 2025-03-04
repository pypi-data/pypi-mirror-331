from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_env_from_source import V1EnvFromSource
from .v1_env_var import V1EnvVar
from .v1_lifecycle import V1Lifecycle
from .v1_probe import V1Probe
from .v1_container_port import V1ContainerPort
from .v1_container_resize_policy import V1ContainerResizePolicy
from .v1_resource_requirements import V1ResourceRequirements
from .v1_security_context import V1SecurityContext
from .v1_volume_device import V1VolumeDevice
from .v1_volume_mount import V1VolumeMount

class V1Container(BaseModel):
    args : Optional[list[str]] = Field(alias = "args", default = None)
    command : Optional[list[str]] = Field(alias = "command", default = None)
    env : Optional[list[V1EnvVar]] = Field(alias = "env", default = None)
    env_from : Optional[list[V1EnvFromSource]] = Field(alias = "envFrom", default = None)
    image : Optional[str] = Field(alias = "image", default = None)
    image_pull_policy : Optional[str] = Field(alias = "imagePullPolicy", default = None)
    lifecycle : Optional[V1Lifecycle] = Field(alias = "lifecycle", default = None)
    liveness_probe : Optional[V1Probe] = Field(alias = "livenessProbe", default = None)
    name : str = Field(alias = "name", default = None)
    ports : Optional[list[V1ContainerPort]] = Field(alias = "ports", default = None)
    readiness_probe : Optional[V1Probe] = Field(alias = "readinessProbe", default = None)
    resize_policy : Optional[list[V1ContainerResizePolicy]] = Field(alias = "resizePolicy", default = None)
    resources : Optional[V1ResourceRequirements] = Field(alias = "resources", default = None)
    restart_policy : Optional[str] = Field(alias = "restartPolicy", default = None)
    security_context : Optional[V1SecurityContext] = Field(alias = "securityContext", default = None)
    startup_probe : Optional[V1Probe] = Field(alias = "startupProbe", default = None)
    stdin : Optional[bool] = Field(alias = "stdin", default = None)
    stdin_once : Optional[bool] = Field(alias = "stdinOnce", default = None)
    termination_message_path : Optional[str] = Field(alias = "terminationMessagePath", default = None)
    termination_message_policy : Optional[str] = Field(alias = "terminationMessagePolicy", default = None)
    tty : Optional[bool] = Field(alias = "tty", default = None)
    volume_devices : Optional[list[V1VolumeDevice]] = Field(alias = "volumeDevices", default = None)
    volume_mounts : Optional[list[V1VolumeMount]] = Field(alias = "volumeMounts", default = None)
    working_dir : Optional[str] = Field(alias = "workingDir", default = None)