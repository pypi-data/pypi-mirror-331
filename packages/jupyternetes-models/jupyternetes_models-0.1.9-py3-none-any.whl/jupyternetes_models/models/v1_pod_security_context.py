from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_app_armor_profile import V1AppArmorProfile
from .v1_selinux_options import V1SELinuxOptions
from .v1_seccomp_profile import V1SeccompProfile 
from .v1_sysctl import V1Sysctl
from .v1_windows_securitycontext_options import V1WindowsSecurityContextOptions


class V1PodSecurityContext(BaseModel):
    app_armor_profile : Optional[V1AppArmorProfile] = Field(default = None, alias="appArmorProfile")
    fs_group : Optional[int] = Field(default = None, alias="fsGroup")
    fs_group_change_policy : Optional[str] = Field(default = None, alias="fsGroupChangePolicy")
    run_as_group : Optional[int] = Field(default = None, alias="runAsGroup")
    run_as_non_root : Optional[bool] = Field(default = None, alias="runAsNonRoot")
    run_as_user : Optional[int] = Field(default = None, alias="runAsUser")
    se_linux_change_policy : Optional[str] = Field(default = None, alias="seLinuxChangePolicy")
    se_linux_options : Optional[V1SELinuxOptions] = Field(default = None, alias="seLinuxOptions")
    seccomp_profile : Optional[V1SeccompProfile] = Field(default = None, alias="seccompProfile")
    supplemental_groups : Optional[list[int]] = Field(default = None, alias="supplementalGroups")
    supplemental_groups_policy : Optional[str] = Field(default = None, alias="supplementalGroupsPolicy")
    sysctls : Optional[list[V1Sysctl]] = Field(default = None, alias="sysctls")
    windows_options : Optional[V1WindowsSecurityContextOptions] = Field(default = None, alias="windowsOptions")