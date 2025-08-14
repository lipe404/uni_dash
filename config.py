import os
import streamlit as st
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (apenas localmente)
load_dotenv()


def get_env_var(name: str) -> str:
    """
    Busca variável de ambiente do .env local ou dos secrets do Streamlit Cloud
    """
    # Primeiro tenta pegar do Streamlit secrets (produção)
    try:
        if hasattr(st, 'secrets') and name in st.secrets:
            return st.secrets[name]
    except Exception as e:
        print(f"Erro ao acessar secrets: {str(e)}")

    # Se não encontrar, tenta pegar das variáveis de ambiente (local)
    value = os.getenv(name)
    if value is None:
        raise ValueError(
            f"Variável de ambiente '{name}' não configurada. "
            f"Por favor, verifique seu arquivo .env local ou os secrets."
        )
    return value


# Configurações das APIs e planilhas
GOOGLE_SHEETS_CONFIG = {
    'planilha_polos': {
        'API_KEY': get_env_var('GOOGLE_SHEETS_POLOS_API_KEY'),
        'SHEET_ID': get_env_var('GOOGLE_SHEETS_POLOS_SHEET_ID'),
        'abas': {
            'polos_ativos': 'POLOS ATIVOS',
            'municipios': 'Sheet3'
        }
    },
    'planilha_vendas': {
        'API_KEY': get_env_var('GOOGLE_SHEETS_VENDAS_API_KEY'),
        'SHEET_ID': get_env_var('GOOGLE_SHEETS_VENDAS_SHEET_ID'),
        'abas': {
            'base_vendas': 'Base de Vendas',
            'dados_parceiros': 'Relação de Parceiros'
        }
    },
    'planilha_alunos': {
        'API_KEY': get_env_var('GOOGLE_SHEETS_ALUNOS_API_KEY'),
        'SHEET_ID': get_env_var('GOOGLE_SHEETS_ALUNOS_SHEET_ID'),
        'abas': {
            'alunos': 'Sheet1'
        }
    }
}
