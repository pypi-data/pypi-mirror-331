from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_affinity import V1Affinity
from .v1_container import V1Container
from .v1_pod_dns_config import V1PodDNSConfig
from .v1_ephemeral_container import V1EphemeralContainer 
from .v1_host_alias import V1HostAlias
from .v1_local_object_reference import V1LocalObjectReference
from .v1_pod_os import V1PodOS
from .v1_pod_readiness_gate import V1PodReadinessGate
from .v1_pod_resource_claim import V1PodResourceClaim
from .v1_resource_requirements import V1ResourceRequirements
from .v1_toleration import V1Toleration
from .v1_topology_spread_constraint import V1TopologySpreadConstraint
from .v1_pod_scheduling_gate import V1PodSchedulingGate
from .v1_pod_security_context import V1PodSecurityContext
from .v1_volume import V1Volume


class V1PodSpec(BaseModel):
    active_deadline_seconds : Optional[int] = Field(default = None, alias = "activeDeadlineSeconds")
    affinity : Optional[V1Affinity] = Field(default = None, alias = "affinity")
    automount_service_account_token : Optional[bool] = Field(default = None, alias = "automountServiceAccountToken")
    containers : list[V1Container] = Field(default = None, alias = "containers")
    dns_config : Optional[V1PodDNSConfig] = Field(default = None, alias = "dnsConfig")
    dns_policy : Optional[str] = Field(default = None, alias = "dnsPolicy")
    enable_service_links : Optional[bool] = Field(default = None, alias = "enableServiceLinks")
    ephemeral_containers : Optional[list[V1EphemeralContainer]] = Field(default = None, alias = "ephemeralContainers")
    host_aliases : Optional[list[V1HostAlias]] = Field(default = None, alias = "hostAliases")
    host_ipc : Optional[bool] = Field(default = None, alias = "hostIPC")
    host_network : Optional[bool] = Field(default = None, alias = "hostNetwork")
    host_pid : Optional[bool] = Field(default = None, alias = "hostPID")
    host_users : Optional[bool] = Field(default = None, alias = "hostUsers")
    hostname : Optional[str] = Field(default = None, alias = "hostname")
    image_pull_secrets : Optional[list[V1LocalObjectReference]] = Field(default = None, alias = "imagePullSecrets")
    init_containers : Optional[list[V1Container]] = Field(default = None, alias = "initContainers")
    node_name : Optional[str] = Field(default = None, alias = "nodeName")
    node_selector : Optional[dict[str,str]] = Field(default = None, alias = "nodeSelector")
    os : Optional[V1PodOS] = Field(default = None, alias = "os")
    overhead : Optional[dict[str,str]] = Field(default = None, alias = "overhead")
    preemption_policy : Optional[str] = Field(default = None, alias = "preemptionPolicy")
    priority : Optional[int] = Field(default = None, alias = "priority")
    priority_class_name : Optional[str] = Field(default = None, alias = "priorityClassName")
    readiness_gates : Optional[list[V1PodReadinessGate]] = Field(default = None, alias = "readinessGates")
    resource_claims : Optional[list[V1PodResourceClaim]] = Field(default = None, alias = "resourceClaims")
    resources : Optional[V1ResourceRequirements] = Field(default = None, alias = "resources")
    restart_policy : Optional[str] = Field(default = None, alias = "restartPolicy")
    runtime_class_name : Optional[str] = Field(default = None, alias = "runtimeClassName")
    scheduler_name : Optional[str] = Field(default = None, alias = "schedulerName")
    scheduling_gates : Optional[list[V1PodSchedulingGate]] = Field(default = None, alias = "schedulingGates")
    security_context : Optional[V1PodSecurityContext] = Field(default = None, alias = "securityContext")
    service_account : Optional[str] = Field(default = None, alias = "serviceAccount")
    service_account_name : Optional[str] = Field(default = None, alias = "serviceAccountName")
    set_hostname_as_fqdn : Optional[bool] = Field(default = None, alias = "setHostnameAsFQDN")
    share_process_namespace : Optional[bool] = Field(default = None, alias = "shareProcessNamespace")
    subdomain : Optional[str] = Field(default = None, alias = "subdomain")
    termination_grace_period_seconds : Optional[int] = Field(default = None, alias = "terminationGracePeriodSeconds")
    tolerations : Optional[list[V1Toleration]] = Field(default = None, alias = "tolerations")
    topology_spread_constraints : Optional[list[V1TopologySpreadConstraint]] = Field(default = None, alias = "topologySpreadConstraints")
    volumes : Optional[list[V1Volume]] = Field(default = None, alias = "volumes")