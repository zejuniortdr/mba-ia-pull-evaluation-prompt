"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt (conteúdo da chave raiz do YAML)

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: '{field}'")

    system_prompt = prompt_data.get("system_prompt", "")
    if isinstance(system_prompt, str):
        system_prompt = system_prompt.strip()
    else:
        system_prompt = ""

    if not system_prompt:
        errors.append("'system_prompt' está vazio")

    if "[TODO]" in system_prompt or "TODO" in system_prompt:
        errors.append("'system_prompt' ainda contém TODOs não resolvidos")

    techniques = prompt_data.get("techniques_applied", [])
    if not isinstance(techniques, list) or len(techniques) < 2:
        errors.append(
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied'. "
            f"Encontradas: {len(techniques) if isinstance(techniques, list) else 0}"
        )

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome completo do prompt no Hub (ex: "username/bug_to_user_story_v2")
        prompt_data: Dados do prompt lidos do YAML (conteúdo da chave raiz)

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_content = prompt_data.get("system_prompt", "")
        user_content = prompt_data.get("user_prompt", "{bug_report}")

        # Garantir que user_prompt tenha a variável de input
        if not user_content or not isinstance(user_content, str):
            user_content = "{bug_report}"

        chat_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(system_content),
                HumanMessagePromptTemplate.from_template(user_content),
            ]
        )

        print(f"  ⬆️  Enviando para o LangSmith Hub: {prompt_name}")

        hub.push(
            prompt_name,
            chat_prompt,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", ""),
        )

        print("  ✓ Prompt publicado com sucesso (público)")
        print(f"  🔗 https://smith.langchain.com/prompts/{prompt_name.split('/')[-1]}")
        return True

    except Exception as e:
        print(f"  ❌ Erro ao fazer push: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    yaml_path = "prompts/bug_to_user_story_v2.yml"

    print(f"📂 Carregando: {yaml_path}")

    yaml_content = load_yaml(yaml_path)
    if not yaml_content:
        print(f"❌ Não foi possível carregar o arquivo '{yaml_path}'")
        print("  Certifique-se de que o arquivo existe antes de continuar.")
        return 1

    # A chave raiz do YAML é o nome do prompt
    prompt_key = "bug_to_user_story_v2"
    prompt_data = yaml_content.get(prompt_key)

    if not prompt_data:
        # Tentar pegar a primeira chave disponível
        keys = list(yaml_content.keys())
        if keys:
            prompt_key = keys[0]
            prompt_data = yaml_content[prompt_key]
            print(f"  ⚠️  Chave '{prompt_key}' encontrada no YAML")
        else:
            print(f"  ❌ Chave '{prompt_key}' não encontrada no YAML")
            return 1

    print(f"  ✓ Prompt '{prompt_key}' carregado")

    # Validar antes de enviar
    print("\n🔍 Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido. Corrija os erros abaixo antes de continuar:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("  ✓ Validação aprovada")

    # Exibir técnicas aplicadas
    techniques = prompt_data.get("techniques_applied", [])
    if techniques:
        print(f"\n🛠️  Técnicas aplicadas ({len(techniques)}):")
        for t in techniques:
            print(f"  - {t}")

    # Push para o Hub
    print()
    prompt_hub_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_hub_name, prompt_data)

    if success:
        print("\n✅ Push concluído com sucesso!")
        print(f"\nPrompt publicado: {prompt_hub_name}")
        print("\nPróximos passos:")
        print("  1. Verifique em: https://smith.langchain.com/prompts")
        print("  2. Execute a avaliação: python src/evaluate.py")
        return 0

    print("\n❌ Falha no push. Verifique os erros acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())