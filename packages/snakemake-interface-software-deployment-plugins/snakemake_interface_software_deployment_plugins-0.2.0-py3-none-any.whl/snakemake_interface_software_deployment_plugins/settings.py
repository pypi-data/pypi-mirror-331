from dataclasses import dataclass


import snakemake_interface_common.plugin_registry.plugin


@dataclass
class SoftwareDeploymentSettingsBase(
    snakemake_interface_common.plugin_registry.plugin.SettingsBase
):
    """Base class for software deployment settings.

    Software deployment plugins can define a subclass of this class,
    named 'SoftwareDeploymentProviderSettings'.
    """

    pass
