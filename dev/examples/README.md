# MCP Tool Call Examples

各アダプターの `execute_tool` リクエスト/レスポンス例を JSON 形式で格納する。

| ファイル | 内容 |
|----------|------|
| discovery.json | list_tools / search_tools / get_tool_info |
| mattersim.json | predict_energy / relax_structure |
| mattergen.json | generate_material |
| mace.json | predict_energy / calculate_forces |
| graphormer.json | predict_property (fairseq evaluate) |
| dig.json | 4 workflow (protein-ligand, protein-system, property-guided, equilibrium) |
| bioemu.json | sample_ensemble |

すべての例は compact mode の `execute_tool` 経由を想定している。
通常モードで個別ツールを直接呼ぶ場合は `arguments` 部分を直接渡す。
