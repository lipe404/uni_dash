import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
# Certifique-se de que load_dotenv() seja chamado antes de tentar acessar as variáveis
load_dotenv()

# Função auxiliar para pegar a variável de ambiente ou retornar um erro claro


def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(
            f"Variável de ambiente '{
                name}' não configurada. Verifique seu arquivo .env.")
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
            'base_vendas': 'Base de Vendas', 'dados_parceiros': 'Relação de Parceiros'
        }
    }
}
