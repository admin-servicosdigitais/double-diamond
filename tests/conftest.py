from pathlib import Path
import sys
import pytest

from src.domain.models.agent_definition import AgentDefinition, ProviderEnum

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_agent_definition():
    return AgentDefinition(
        id="1-explorer",
        stage="1-explorer",
        name="Explorer Agent",
        description="Explores business opportunities",
        role="explorer",
        model="gpt-4",
        provider=ProviderEnum.OPENAI,
        summary_format="markdown",
        instructions_md="# Explorer Instructions\nExplore the given topics and identify opportunities.",
        tools=["web_search", "data_analysis"],
        execution_mode="single_pass",
        max_steps=1,
    )


@pytest.fixture
def sample_workflow_input():
    return {
        "temas": ["fintech", "healthcare"],
        "segmento": "SME",
        "dominio": "fintech",
    }
