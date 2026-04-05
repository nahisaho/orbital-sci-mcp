from __future__ import annotations

from collections.abc import Callable

from .adapters import BioEmuAdapter, DigAdapter, GraphormerAdapter, MaceAdapter, MatterGenAdapter, MatterSimAdapter
from .models import DependencyRequirement, ToolSpec
from .schemas.materials import MaterialGenerationInput, MaterialStructureInput
from .schemas.molecules import MoleculeInput
from .schemas.proteins import ProteinSequenceInput


DISCOVERY_TOOL_NAMES = ["list_tools", "get_tool_info", "search_tools", "execute_tool"]


class ToolRegistry:
    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}
        self._adapter_factories: dict[str, Callable[[], object]] = {}
        self._enabled_domains: set[str] = set()
        self._enabled_tools: set[str] = set()
        self._disabled_tools: set[str] = set()

    def register(self, spec: ToolSpec) -> None:
        self._specs[spec.name] = spec

    def register_adapter(self, key: str, factory: Callable[[], object]) -> None:
        self._adapter_factories[key] = factory

    def configure(
        self,
        *,
        enabled_domains: list[str] | None = None,
        enabled_tools: list[str] | None = None,
        disabled_tools: list[str] | None = None,
    ) -> None:
        self._enabled_domains = set(enabled_domains or [])
        self._enabled_tools = set(enabled_tools or [])
        self._disabled_tools = set(disabled_tools or [])

    def get(self, name: str) -> ToolSpec:
        return self._specs[name]

    def list_all(self) -> list[ToolSpec]:
        return [spec for spec in self._specs.values() if self._is_enabled(spec)]

    def list_public_tools(self, compact_mode: bool = False) -> list[ToolSpec]:
        return self.list_all()

    def search(self, query: str, domain: str | None = None) -> list[ToolSpec]:
        query_lower = query.lower()
        results = []
        for spec in self.list_all():
            if domain and spec.domain != domain:
                continue
            if query_lower in spec.name.lower() or query_lower in spec.description.lower():
                results.append(spec)
        return results

    def create_adapter(self, name: str):
        spec = self.get(name)
        factory = self._adapter_factories[spec.adapter_key]
        return factory()

    def _is_enabled(self, spec: ToolSpec) -> bool:
        if spec.name in self._disabled_tools:
            return False
        if self._enabled_tools and spec.name not in self._enabled_tools:
            return False
        if self._enabled_domains and spec.domain not in self._enabled_domains:
            return False
        return True


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register_adapter("mattersim", MatterSimAdapter)
    registry.register_adapter("mattergen", MatterGenAdapter)
    registry.register_adapter("mace", MaceAdapter)
    registry.register_adapter("graphormer", GraphormerAdapter)
    registry.register_adapter("dig", DigAdapter)
    registry.register_adapter("bioemu", BioEmuAdapter)

    specs = [
        ToolSpec(
            name="mattersim_predict_energy",
            description="Predict material energy from a structure input.",
            domain="materials",
            tags=["tier1", "materials"],
            input_model=MaterialStructureInput,
            adapter_key="mattersim",
            dependency_requirements=DependencyRequirement(python_packages=["mattersim"]),
        ),
        ToolSpec(
            name="mattersim_relax_structure",
            description="Relax a material structure with MatterSim.",
            domain="materials",
            tags=["tier1", "materials"],
            input_model=MaterialStructureInput,
            adapter_key="mattersim",
            dependency_requirements=DependencyRequirement(python_packages=["mattersim"]),
        ),
        ToolSpec(
            name="mattergen_generate_material",
            description="Generate material candidates with MatterGen.",
            domain="materials",
            tags=["tier1", "materials", "generation"],
            input_model=MaterialGenerationInput,
            adapter_key="mattergen",
            dependency_requirements=DependencyRequirement(python_packages=["mattergen"]),
        ),
        ToolSpec(
            name="mace_predict_energy",
            description="Predict material energy with MACE.",
            domain="materials",
            tags=["tier1", "materials"],
            input_model=MaterialStructureInput,
            adapter_key="mace",
            dependency_requirements=DependencyRequirement(python_packages=["mace"]),
        ),
        ToolSpec(
            name="mace_calculate_forces",
            description="Calculate atomic forces with MACE.",
            domain="materials",
            tags=["tier1", "materials"],
            input_model=MaterialStructureInput,
            adapter_key="mace",
            dependency_requirements=DependencyRequirement(python_packages=["mace"]),
        ),
        ToolSpec(
            name="graphormer_predict_property",
            description="Predict molecular properties with Graphormer.",
            domain="molecules",
            tags=["tier1", "molecules"],
            input_model=MoleculeInput,
            adapter_key="graphormer",
            dependency_requirements=DependencyRequirement(python_packages=["graphormer"]),
        ),
        ToolSpec(
            name="dig_sample_conformations",
            description="Generate protein-ligand conformations with DiG task workflows.",
            domain="molecules",
            tags=["tier1", "molecules"],
            input_model=MoleculeInput,
            adapter_key="dig",
            dependency_requirements=DependencyRequirement(
                env_vars=[],
                artifacts=[
                    "distributional_graphormer/protein-ligand/evaluation/single_datapoint_sampling.sh"
                ],
            ),
        ),
        ToolSpec(
            name="dig_predict_equilibrium",
            description="Run DiG equilibrium density workflows for catalyst-adsorption systems.",
            domain="molecules",
            tags=["tier1", "molecules", "equilibrium"],
            input_model=MoleculeInput,
            adapter_key="dig",
            dependency_requirements=DependencyRequirement(
                artifacts=[
                    "distributional_graphormer/catalyst-adsorption/scripts/density.sh"
                ],
            ),
        ),
        ToolSpec(
            name="bioemu_sample_ensemble",
            description="Sample protein structure ensembles with BioEmu.",
            domain="proteins",
            tags=["tier1", "proteins"],
            input_model=ProteinSequenceInput,
            adapter_key="bioemu",
            dependency_requirements=DependencyRequirement(
                python_packages=["bioemu"],
                gpu_required=True,
            ),
        ),
    ]
    for spec in specs:
        registry.register(spec)
    return registry
