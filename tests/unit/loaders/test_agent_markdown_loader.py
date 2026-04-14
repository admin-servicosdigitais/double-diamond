from pathlib import Path

from src.loaders.agent_markdown_loader import AgentMarkdownLoader


def test_parse_output_artifacts_from_instructions(tmp_path: Path) -> None:
    agent_dir = tmp_path / "1-explorer"
    agent_dir.mkdir(parents=True, exist_ok=True)
    agent_file = agent_dir / "agent.md"
    agent_file.write_text(
        """---
name: explorer
stage: "1"
---

# Agente
## Artefatos de saida
1. **Radar de Oportunidades** (TMPL-000)
2. **Conceito Escolhido + Trade-offs** (TMPL-009)

## Ao finalizar
Gerar resumo.
""",
        encoding="utf-8",
    )

    loader = AgentMarkdownLoader(agents_path=tmp_path)
    definition = loader.load_by_id("1-explorer")

    assert definition is not None
    assert definition.output_artifacts == [
        "Radar de Oportunidades",
        "Conceito Escolhido + Trade-offs",
    ]
