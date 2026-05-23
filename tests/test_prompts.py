"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_prompt_data() -> dict:
    """Retorna os dados do prompt v2 (chave raiz extraída)."""
    raw = load_prompts(str(PROMPT_V2_PATH))
    # A chave raiz pode ser 'bug_to_user_story_v2' ou similar
    key = "bug_to_user_story_v2"
    if key in raw:
        return raw[key]
    # Fallback: pegar a primeira chave
    return next(iter(raw.values()))


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        data = get_prompt_data()
        assert "system_prompt" in data, "Campo 'system_prompt' não encontrado no YAML"
        system_prompt = data["system_prompt"]
        assert system_prompt is not None, "'system_prompt' é None"
        assert isinstance(system_prompt, str), "'system_prompt' deve ser uma string"
        assert len(system_prompt.strip()) > 0, "'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "")
        
        role_indicators = [
            "você é",
            "voce é",
            "você é um",
            "you are",
            "como um especialista",
            "sua função é",
            "seu papel é",
            "atuando como",
        ]
        
        system_lower = system_prompt.lower()
        has_role = any(indicator in system_lower for indicator in role_indicators)
        
        assert has_role, (
            "O system_prompt não define uma persona/role. "
            "Inclua algo como 'Você é um Product Manager experiente...'"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "")
        
        format_indicators = [
            "markdown",
            "user story",
            "como um",
            "eu quero",
            "para que",
            "critérios de aceitação",
            "acceptance criteria",
            "given",
            "when",
            "then",
            "##",
            "**",
        ]
        
        system_lower = system_prompt.lower()
        has_format = any(indicator in system_lower for indicator in format_indicators)
        
        assert has_format, (
            "O prompt não menciona o formato esperado de saída. "
            "Inclua instruções de formato Markdown ou a estrutura de User Story."
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "")
        
        few_shot_indicators = [
            "exemplo",
            "example",
            "entrada:",
            "saída:",
            "input:",
            "output:",
            "bug report:",
            "user story:",
            "---\n",
            "===",
        ]
        
        system_lower = system_prompt.lower()
        has_examples = any(indicator in system_lower for indicator in few_shot_indicators)
        
        # Checar também se há pelo menos 2 ocorrências de padrões de exemplo
        count = sum(1 for ind in few_shot_indicators if ind in system_lower)
        
        assert has_examples and count >= 2, (
            "O prompt não contém exemplos Few-shot suficientes. "
            "Adicione pelo menos 2 exemplos de entrada/saída ao system_prompt."
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        data = get_prompt_data()
        system_prompt = data.get("system_prompt", "")
        user_prompt = data.get("user_prompt", "")
        description = data.get("description", "")
        
        full_text = f"{system_prompt}\n{user_prompt}\n{description}"
        
        assert "[TODO]" not in full_text, "Encontrado '[TODO]' no prompt. Remova antes de fazer push."
        assert "TODO" not in full_text, "Encontrado 'TODO' no prompt. Remova antes de fazer push."

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        data = get_prompt_data()
        
        assert "techniques_applied" in data, (
            "Campo 'techniques_applied' não encontrado no YAML. "
            "Adicione a lista de técnicas aplicadas nos metadados."
        )
        
        techniques = data["techniques_applied"]
        
        assert isinstance(techniques, list), "'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}. "
            "Adicione mais técnicas em 'techniques_applied'."
        )
        
        # Verificar que as técnicas não estão vazias
        non_empty = [t for t in techniques if t and str(t).strip()]
        assert len(non_empty) >= 2, (
            "As técnicas em 'techniques_applied' não podem estar vazias."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])