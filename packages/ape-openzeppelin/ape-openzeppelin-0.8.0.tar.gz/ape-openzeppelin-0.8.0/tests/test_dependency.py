import pytest

from ape_openzeppelin.dependency import OpenZeppelinDependency
from ape_openzeppelin.utils import VERSIONS


class TestOpenZeppelinDependency:
    @pytest.fixture
    def dependency(self):
        return OpenZeppelinDependency(openzeppelin="4.0.0")

    def test_version_id(self, dependency):
        assert dependency.version_id == "4.0.0"

    def test_uri(self, dependency):
        assert (
            dependency.uri
            == "https://github.com/OpenZeppelin/openzeppelin-contracts/releases/tag/v4.0.0"
        )

    def test_name(self, dependency):
        assert dependency.name == "openzeppelin"
        # Also show we can change it.
        other = OpenZeppelinDependency(name="MyOpenZeppelin", openzeppelin="4.0.0")
        expected = "myopenzeppelin"  # PackageName validation lowers them.
        assert other.name == expected

    @pytest.mark.parametrize("version", VERSIONS)
    def test_integration(self, version, project):
        dependency = project.dependencies.get_dependency("openzeppelin", version)
        assert dependency.install()
        assert dependency.compile()
