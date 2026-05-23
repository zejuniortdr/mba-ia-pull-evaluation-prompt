"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull dos prompts do LangSmith Hub e salva localmente.

    Returns:
        bool: True se sucesso, False caso contrário
    """
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    prompt_hub_name = "leonanluppi/bug_to_user_story_v1"
    output_path = "prompts/bug_to_user_story_v1.yml"

    try:
        print(f"⬇️  Fazendo pull: {prompt_hub_name}")
        prompt = hub.pull(prompt_hub_name)
        print("  ✓ Prompt carregado do LangSmith Hub")

        # Extrair mensagens do ChatPromptTemplate
        messages = prompt.messages
        system_prompt = ""
        user_prompt = ""

        for msg in messages:
            role = msg.__class__.__name__.lower()
            content = msg.prompt.template if hasattr(msg, "prompt") else str(msg)

            if "system" in role:
                system_prompt = content
            elif "human" in role:
                user_prompt = content

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Usar yaml diretamente para preservar literais de string com |
        import yaml

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(prompt_data, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)

        print(f"  ✓ Prompt salvo em: {output_path}")
        return True

    except Exception as e:
        print(f"\n❌ Erro ao fazer pull do prompt '{prompt_hub_name}': {e}")
        print("\nVerifique:")
        print("  - LANGSMITH_API_KEY está configurada corretamente no .env")
        print("  - Você tem conexão com a internet")
        print(f"  - O prompt '{prompt_hub_name}' existe no LangSmith Hub")
        return False


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()

    if success:
        print("\n✅ Pull concluído com sucesso!")
        print("\nPróximos passos:")
        print("  1. Analise o prompt em prompts/bug_to_user_story_v1.yml")
        print("  2. Crie sua versão otimizada em prompts/bug_to_user_story_v2.yml")
        print("  3. Execute: python src/push_prompts.py")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())