from src.application.services.prompt_assembler import PromptAssembler
from src.domain.models.agent_definition import AgentDefinition


class TestPromptAssembler:
    def test_build_basic_prompt(self):
        agent = AgentDefinition(
            id="1-explorer",
            stage="1-explorer",
            name="Explorer",
            description="Explores",
            role="explorer",
            model="gpt-4",
            summary_format="markdown",
            instructions_md="# Instructions\nExplore topics",
        )
        assembler = PromptAssembler()
        result = assembler.build(agent)
        assert "# Agent Instructions" in result
        assert "# Instructions\nExplore topics" in result

    def test_build_with_previous_compact(self):
        agent = AgentDefinition(
            id="2-intake",
            stage="2-intake",
            name="Intake",
            description="Intakes",
            role="intake",
            model="gpt-4",
            summary_format="markdown",
            instructions_md="Process input",
        )
        assembler = PromptAssembler()
        result = assembler.build(agent, previous_compact="Previous output here")
        assert "# Previous Stage (N-1) Compact Output" in result
        assert "Previous output here" in result

    def test_build_with_context_string(self):
        agent = AgentDefinition(
            id="1-explorer",
            stage="1-explorer",
            name="Explorer",
            description="Explores",
            role="explorer",
            model="gpt-4",
            summary_format="markdown",
            instructions_md="Instructions",
        )
        assembler = PromptAssembler()
        result = assembler.build(agent, context="Additional context")
        assert "# Additional User Context" in result
        assert "Additional context" in result

    def test_build_with_context_dict(self):
        agent = AgentDefinition(
            id="1-explorer",
            stage="1-explorer",
            name="Explorer",
            description="Explores",
            role="explorer",
            model="gpt-4",
            summary_format="markdown",
            instructions_md="Instructions",
        )
        assembler = PromptAssembler()
        context = {"priority": "high", "deadline": "today"}
        result = assembler.build(agent, context=context)
        assert "# Additional User Context" in result
        assert "- priority: high" in result
        assert "- deadline: today" in result

    def test_build_with_full_outputs(self):
        agent = AgentDefinition(
            id="8-prototype-visual",
            stage="8-prototype-visual",
            name="Prototype Visual",
            description="Creates visuals",
            role="visualizer",
            model="gpt-4",
            summary_format="markdown",
            instructions_md="Create prototypes",
        )
        assembler = PromptAssembler()
        full_outputs = {
            "file1.md": "Content 1",
            "file2.md": "Content 2",
        }
        result = assembler.build(
            agent,
            previous_full_outputs=full_outputs,
            include_full_previous_stage=True,
        )
        assert "# Previous Stage (N-1) Full Outputs" in result
        assert "## file1.md\nContent 1" in result
        assert "## file2.md\nContent 2" in result

    def test_normalize_context_string(self):
        result = PromptAssembler._normalize_context("  test context  ")
        assert result == "test context"

    def test_normalize_context_dict(self):
        context = {"key1": "value1", "key2": "value2"}
        result = PromptAssembler._normalize_context(context)
        assert "key1: value1" in result
        assert "key2: value2" in result

    def test_format_full_outputs(self):
        outputs = {
            "b-file.md": "Content B",
            "a-file.md": "Content A",
        }
        result = PromptAssembler._format_full_outputs(outputs)
        # Should be sorted by filename
        assert "## a-file.md" in result
        assert "## b-file.md" in result
        assert "Content A" in result
        assert "Content B" in result