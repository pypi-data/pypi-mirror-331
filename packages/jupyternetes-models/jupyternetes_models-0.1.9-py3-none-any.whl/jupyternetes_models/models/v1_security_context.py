from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_app_armor_profile import V1AppArmorProfile
from .v1_capabilities import V1Capabilities
from .v1_selinux_options import V1SELinuxOptions
from .v1_seccomp_profile import V1SeccompProfile
from .v1_windows_securitycontext_options import V1WindowsSecurityContextOptions


class V1SecurityContext(BaseModel):
    allow_privilege_escalation : Optional[bool] = Field(default = None, alias = "allowPrivilegeEscalation")
    app_armor_profile : Optional[V1AppArmorProfile] = Field(default = None, alias = "appArmorProfile")
    capabilities : Optional[V1Capabilities] = Field(default = None, alias = "capabilities")
    privileged : Optional[bool] = Field(default = None, alias = "privileged")
    proc_mount : Optional[str] = Field(default = None, alias = "procMount")
    read_only_root_filesystem : Optional[bool] = Field(default = None, alias = "readOnlyRootFilesystem")
    run_as_group : Optional[int] = Field(default = None, alias = "runAsGroup")
    run_as_non_root : Optional[bool] = Field(default = None, alias = "runAsNonRoot")
    run_as_user : Optional[int] = Field(default = None, alias = "runAsUser")
    se_linux_options : Optional[V1SELinuxOptions] = Field(default = None, alias = "seLinuxOptions")
    seccomp_profile : Optional[V1SeccompProfile] = Field(default = None, alias = "seccompProfile")
    windows_options : Optional[V1WindowsSecurityContextOptions] = Field(default = None, alias = "windowsOptions")