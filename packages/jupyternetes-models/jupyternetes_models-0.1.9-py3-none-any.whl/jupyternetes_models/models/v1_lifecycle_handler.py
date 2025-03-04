from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_exec_action import V1ExecAction
from .v1_http_get_action import V1HTTPGetAction
from .v1_sleep_action import V1SleepAction
from .v1_tcp_socket_action import V1TCPSocketAction 


class V1LifecycleHandler(BaseModel):
    exec_action : Optional[V1ExecAction] = Field(default = None, alias = "_exec")
    http_get : Optional[V1HTTPGetAction] = Field(default = None, alias = "httpGet")
    sleep : Optional[V1SleepAction] = Field(default = None, alias = "sleep")
    tcp_socket : Optional[V1TCPSocketAction] = Field(default = None, alias = "tcpSocket")