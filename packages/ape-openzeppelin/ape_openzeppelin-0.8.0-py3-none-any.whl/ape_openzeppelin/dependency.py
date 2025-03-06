from pathlib import Path
from typing import TYPE_CHECKING

from ape.api import DependencyAPI
from ape_pm.dependency import GithubDependency

from ape_openzeppelin.utils import VERSIONS

if TYPE_CHECKING:
    from ethpm_types import PackageManifest


class OpenZeppelinDependency(DependencyAPI):
    name: str = "openzeppelin"
    openzeppelin: str

    @property
    def github(self) -> GithubDependency:
        version = self.openzeppelin
        data = {"name": self.name, "github": "OpenZeppelin/openzeppelin-contracts"}

        # Some versions are only available via reference.
        settings: dict = VERSIONS.get(version) or {}
        version_key = settings.get("version_key", "version")
        data[version_key] = version

        # Use defaults from plugin to get this version of OZ to work out-of-the-box.
        if config_override := settings.get("config_override"):
            self.config_override = data["config_override"] = config_override

        return GithubDependency.model_validate(data)

    @property
    def version_id(self) -> str:
        return self.github.version_id

    @property
    def uri(self) -> str:
        return self.github.uri

    @property
    def package_id(self) -> str:
        return self.github.package_id

    def fetch(self, destination: Path) -> "PackageManifest":
        return self.github.fetch(destination)
