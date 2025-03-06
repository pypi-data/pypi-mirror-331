__author__ = "Johannes Köster"
__copyright__ = "Copyright 2024, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field, fields
import hashlib
from pathlib import Path
import sys
from typing import Any, ClassVar, Dict, Optional, Tuple, Type
import subprocess as sp

from snakemake_interface_software_deployment_plugins.settings import (
    SoftwareDeploymentSettingsBase,
)


_MANAGED_FIELDS = {
    "settings",
    "_managed_hash_store",
    "_managed_deployment_hash_store",
    "_obj_hash",
}


@dataclass
class EnvSpecBase(ABC):
    within: Optional["EnvSpecBase"]
    fallback: Optional["EnvSpecBase"]

    @classmethod
    def env_cls(cls):
        return sys.modules[__name__].EnvBase

    def __or__(self, other: "EnvSpecBase") -> "EnvSpecBase":
        copied = copy(self)
        copied.fallback = other
        return copied


@dataclass
class EnvBase:
    spec: EnvSpecBase
    within: Optional["EnvBase"]
    settings: Optional[SoftwareDeploymentSettingsBase]
    _managed_hash_store: Optional[str] = field(init=False, default=None)
    _managed_deployment_hash_store: Optional[str] = field(init=False, default=None)
    _obj_hash: Optional[int] = field(init=False, default=None)
    _cache: ClassVar[Dict[Tuple[Type["EnvBase"], Optional["EnvBase"]], Any]] = {}

    def __post_init__(self) -> None:  # noqa B027
        """Do stuff after object initialization."""
        pass

    @staticmethod
    def once(func):
        """Decorator to cache the result of a method call that shall be only
        executed once per combination of plugin and "within" environment.
        """

        def wrapper(self, *args, **kwargs):
            key = (self.__class__, self.within)
            if key in self._cache:
                return self._cache[key]
            value = func(self, *args, **kwargs)
            self._cache[key] = value
            return value

        return wrapper

    @abstractmethod
    def decorate_shellcmd(self, cmd: str) -> str:
        """Decorate given shell command such that it runs within the environment,
        using self.spec.
        """
        ...

    @abstractmethod
    def record_hash(self, hash_object) -> None:
        """Update given hash object such that it changes whenever the environment
        specified via self.spec could potentially contain a different set of
        software (in terms of versions or packages).
        """
        ...

    def run_cmd(self, cmd: str, **kwargs) -> sp.CompletedProcess:
        """Run a command while potentially respecting the self.within environment,
        returning the result of subprocess.run.

        kwargs is passed to subprocess.run, shell=True is always set.
        """
        if self.within is not None:
            cmd = self.within.managed_decorate_shellcmd(cmd)
        return sp.run(cmd, shell=True, **kwargs)

    def managed_decorate_shellcmd(self, cmd: str) -> str:
        cmd = self.decorate_shellcmd(cmd)
        if self.within is not None:
            cmd = self.within.managed_decorate_shellcmd(cmd)
        return cmd

    def hash(self) -> str:
        return self._managed_generic_hash("hash")

    def _managed_generic_hash(self, kind: str) -> str:
        store = getattr(self, f"_managed_{kind}_store")
        if store is None:
            record_hash = f"record_{kind}"
            hash_object = hashlib.md5()
            if self.within is not None:
                getattr(self.within, record_hash)(hash_object)
            getattr(self, record_hash)(hash_object)
            store = hash_object.hexdigest()
        return store

    def __hash__(self) -> int:
        # take the hash of all fields by settings, _managed_hash_store and _managed_deployment_hash_store
        if self._obj_hash is None:
            self._obj_hash = hash(
                tuple(
                    getattr(self, field.name)
                    for field in fields(self)
                    if field.name not in _MANAGED_FIELDS
                )
            )
        return self._obj_hash

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and all(
            getattr(self, field.name) == getattr(other, field.name)
            for field in fields(self)
            if field.name not in _MANAGED_FIELDS
        )


@dataclass
class DeployableEnvBase(EnvBase):
    _deployment_prefix: Optional[Path] = None

    @abstractmethod
    def deploy(self) -> None:
        """Deploy the environment to self.deployment_path.

        When issuing shell commands, the environment should use
        self.provider.run(cmd: str) in order to ensure that it runs within eventual
        parent environments (e.g. a container or an env module).
        """
        ...

    @abstractmethod
    def record_deployment_hash(self, hash_object) -> None:
        """Update given hash such that it changes whenever the environment
        needs to be redeployed, e.g. because its content has changed or the
        deployment location has changed. The latter is only relevant if the
        deployment is senstivive to the path (e.g. in case of conda, which patches
        the RPATH in binaries).
        """
        ...

    @abstractmethod
    def remove(self) -> None:
        """Remove the deployed environment."""
        ...

    def managed_deploy(self) -> None:
        if isinstance(self, ArchiveableEnvBase) and self.archive_path.exists():
            self.deploy_from_archive()
        else:
            self.deploy()

    def deployment_hash(self) -> str:
        return self._managed_generic_hash("deployment_hash")

    @property
    def deployment_path(self) -> Path:
        return self.provider.deployment_prefix / self.deployment_hash()


class ArchiveableEnvBase(EnvBase):
    archive_prefix: Optional[Path] = None

    @abstractmethod
    def archive(self) -> None:
        """Archive the environment to self.archive_path.

        When issuing shell commands, the environment should use
        self.provider.run(cmd: str) in order to ensure that it runs within eventual
        parent environments (e.g. a container or an env module).
        """
        ...

    @abstractmethod
    def deploy_from_archive(self) -> None:
        """Deploy the environment from an archive."""
        ...

    @property
    def archive_path(self) -> Path:
        return self.archive_prefix / self.hash()
