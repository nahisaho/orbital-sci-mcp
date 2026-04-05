from __future__ import annotations

from ..registry import ToolRegistry


def build_list_tools(registry: ToolRegistry, compact_mode: bool):
    def list_tools(domain: str | None = None, available_only: bool = False) -> list[dict]:
        items = []
        for spec in registry.list_all():
            if domain and spec.domain != domain:
                continue
            availability = registry.create_adapter(spec.name).check_availability()
            if available_only and not availability.available:
                continue
            items.append(
                {
                    "name": spec.name,
                    "description": spec.description,
                    "domain": spec.domain,
                    "available": availability.available,
                    "availability_status": availability.status,
                }
            )
        if compact_mode:
            return [
                {
                    "compact_mode": True,
                    "discovery_tools": ["list_tools", "get_tool_info", "search_tools", "execute_tool"],
                    "registered_tool_count": len(items),
                    "tools": items,
                }
            ]
        return items

    return list_tools


def build_get_tool_info(registry: ToolRegistry):
    def get_tool_info(tool_name: str) -> dict:
        spec = registry.get(tool_name)
        availability = registry.create_adapter(tool_name).check_availability()
        return {
            "name": spec.name,
            "description": spec.description,
            "domain": spec.domain,
            "tags": spec.tags,
            "maturity": spec.maturity,
            "dependency_requirements": spec.dependency_requirements.model_dump(),
            "availability": availability.model_dump(),
            "input_schema": spec.input_model.model_json_schema(),
        }

    return get_tool_info


def build_search_tools(registry: ToolRegistry):
    def search_tools(query: str, domain: str | None = None, limit: int = 10) -> list[dict]:
        matches = registry.search(query=query, domain=domain)
        return [
            {"name": spec.name, "description": spec.description, "domain": spec.domain}
            for spec in matches[:limit]
        ]

    return search_tools
