from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_aws_elasticblockstore_volumesource import V1AWSElasticBlockStoreVolumeSource
from .v1_azure_disk_volumesource import V1AzureDiskVolumeSource
from .v1_azure_file_volumesource import V1AzureFileVolumeSource
from .v1_cephfs_volumesource import V1CephFSVolumeSource
from .v1_cinder_volumesource import V1CinderVolumeSource
from .v1_config_map_volumesource import V1ConfigMapVolumeSource
from .v1_csi_volumesource import V1CSIVolumeSource
from .v1_downwardapi_volumesource import V1DownwardAPIVolumeSource
from .v1_emptydir_volumesource import V1EmptyDirVolumeSource
from .v1_ephemeral_volumesource import V1EphemeralVolumeSource
from .v1_fc_volumesource import V1FCVolumeSource
from .v1_flex_volumesource import V1FlexVolumeSource
from .v1_flocker_volumesource import V1FlockerVolumeSource
from .v1_gce_persistentdisk_volumesource import V1GCEPersistentDiskVolumeSource
from .v1_glusterfs_volumesource import V1GlusterfsVolumeSource
from .v1_hostpath_volumesource import V1HostPathVolumeSource
from .v1_image_volumesource import V1ImageVolumeSource
from .v1_iscsi_volumesource import V1ISCSIVolumeSource
from .v1_nfs_volumesource import V1NFSVolumeSource
from .v1_persistentvolumeclaim_volumesource import V1PersistentVolumeClaimVolumeSource
from .v1_photonpersistentdisk_volumesource import V1PhotonPersistentDiskVolumeSource
from .v1_portworx_volumesource import V1PortworxVolumeSource
from .v1_projected_volumesource import V1ProjectedVolumeSource
from .v1_quobyte_volumesource import V1QuobyteVolumeSource
from .v1_rbd_volumesource import V1RBDVolumeSource
from .v1_scaleio_volumesource import V1ScaleIOVolumeSource
from .v1_secret_volumesource import V1SecretVolumeSource
from .v1_storageos_volumesource import V1StorageOSVolumeSource
from .v1_vsphere_virtualdisk_volumesource import V1VsphereVirtualDiskVolumeSource


class V1Volume(BaseModel):
    aws_elastic_block_store : Optional[V1AWSElasticBlockStoreVolumeSource] = Field(default = None, alias = "awsElasticBlockStore")
    azure_disk : Optional[V1AzureDiskVolumeSource] = Field(default = None, alias = "azureDisk")
    azure_file : Optional[V1AzureFileVolumeSource] = Field(default = None, alias = "azureFile")
    cephfs : Optional[V1CephFSVolumeSource] = Field(default = None, alias = "cephfs")
    cinder : Optional[V1CinderVolumeSource] = Field(default = None, alias = "cinder")
    config_map : Optional[V1ConfigMapVolumeSource] = Field(default = None, alias = "configMap")
    csi : Optional[V1CSIVolumeSource] = Field(default = None, alias = "csi")
    downward_api : Optional[V1DownwardAPIVolumeSource] = Field(default = None, alias = "downwardAPI")
    empty_dir : Optional[V1EmptyDirVolumeSource] = Field(default = None, alias = "emptyDir")
    ephemeral : Optional[V1EphemeralVolumeSource] = Field(default = None, alias = "ephemeral")
    fc : Optional[V1FCVolumeSource] = Field(default = None, alias = "fc")
    flex_volume : Optional[V1FlexVolumeSource] = Field(default = None, alias = "flexVolume")
    flocker : Optional[V1FlockerVolumeSource] = Field(default = None, alias = "flocker")
    gce_persistent_disk : Optional[V1GCEPersistentDiskVolumeSource] = Field(default = None, alias = "gcePersistentDisk")
    glusterfs : Optional[V1GlusterfsVolumeSource] = Field(default = None, alias = "glusterfs")
    host_path : Optional[V1HostPathVolumeSource] = Field(default = None, alias = "hostPath")
    image : Optional[V1ImageVolumeSource] = Field(default = None, alias = "image")
    iscsi : Optional[V1ISCSIVolumeSource] = Field(default = None, alias = "iscsi")
    name : str = Field(default = None, alias = "name")
    nfs : Optional[V1NFSVolumeSource] = Field(default = None, alias = "nfs")
    persistent_volume_claim : Optional[V1PersistentVolumeClaimVolumeSource] = Field(default = None, alias = "persistentVolumeClaim")
    photon_persistent_disk : Optional[V1PhotonPersistentDiskVolumeSource] = Field(default = None, alias = "photonPersistentDisk")
    portworx_volume : Optional[V1PortworxVolumeSource] = Field(default = None, alias = "portworxVolume")
    projected : Optional[V1ProjectedVolumeSource] = Field(default = None, alias = "projected")
    quobyte : Optional[V1QuobyteVolumeSource] = Field(default = None, alias = "quobyte")
    rbd : Optional[V1RBDVolumeSource] = Field(default = None, alias = "rbd")
    scale_io : Optional[V1ScaleIOVolumeSource] = Field(default = None, alias = "scaleIO")
    secret : Optional[V1SecretVolumeSource] = Field(default = None, alias = "secret")
    storageos : Optional[V1StorageOSVolumeSource] = Field(default = None, alias = "storageos")
    vsphere_volume : Optional[V1VsphereVirtualDiskVolumeSource] = Field(default = None, alias = "vsphereVolume")