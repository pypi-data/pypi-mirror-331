from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_exec_action import V1ExecAction
from .v1_http_get_action import V1HTTPGetAction
from .v1_grpc_action import V1GRPCAction
from .v1_tcp_socket_action import V1TCPSocketAction


class V1Probe(BaseModel):
    exec_action : Optional[V1ExecAction] = Field(default = None, alias="_exec")
    failure_threshold : Optional[int] = Field(default = None, alias="failureThreshold")
    grpc : Optional[V1GRPCAction] = Field(default = None, alias="grpc")
    http_get : Optional[V1HTTPGetAction] = Field(default = None, alias="httpGet")
    initial_delay_seconds : Optional[int] = Field(default = None, alias="initialDelaySeconds")
    period_seconds : Optional[int] = Field(default = None, alias="periodSeconds")
    success_threshold : Optional[int] = Field(default = None, alias="successThreshold")
    tcp_socket : Optional[V1TCPSocketAction] = Field(default = None, alias="tcpSocket")
    termination_grace_period_seconds : Optional[int] = Field(default = None, alias="terminationGracePeriodSeconds")
    timeout_seconds : Optional[int] = Field(default = None, alias="timeoutSeconds")