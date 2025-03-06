__author__ = "Johannes Köster"
__copyright__ = "Copyright 2024, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass
from typing import Optional, Type
from snakemake_interface_software_deployment_plugins import EnvBase, EnvSpecBase
from snakemake_interface_software_deployment_plugins.settings import (
    SoftwareDeploymentSettingsBase,
)
import snakemake_interface_software_deployment_plugins._common as common

from snakemake_interface_common.plugin_registry.plugin import PluginBase


@dataclass
class Plugin(PluginBase):
    _software_deployment_settings_cls: Optional[Type[SoftwareDeploymentSettingsBase]]
    _env_cls: Type[EnvBase]
    _env_spec_cls: Type[EnvSpecBase]
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def cli_prefix(self):
        return "sdm-" + self._only_name

    @property
    def _only_name(self):
        return self.name.replace(common.software_deployment_plugin_module_prefix, "")

    @property
    def settings_cls(self):
        return self._software_deployment_settings_cls

    @property
    def env_cls(self):
        return self._env_cls

    @property
    def env_spec_cls(self):
        return self._env_spec_cls
