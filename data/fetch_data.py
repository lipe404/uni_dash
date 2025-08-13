# data/fetch_data.py
"""
Módulo principal de fetch de dados - Importa todas as funções dos submódulos
"""

# Importar funções da API do Google Sheets
from .sheets_api import (
    fetch_google_sheet_data,
    fetch_parceiros_data,
    fetch_vendas_publicas
)

# Importar funções de dados de parceiros
from .partner_data import (
    get_parceiro_vendas_data,
    get_parceiro_vendas_detalhadas,
    get_modalidades_parceiro_filtradas,
    get_cursos_parceiro_filtrados,
    get_lista_modalidades_parceiro,
    get_modalidades_parceiro,
    get_cursos_parceiro,
    get_modalidades_parceiro_unica
)

# Importar funções de evolução
from .evolution_data import (
    get_evolucao_matriculas_parceiro
)

# Importar funções de estatísticas
from .statistics_data import (
    get_estatisticas_parceiro,
    get_estatisticas_parceiro_filtradas
)

# Importar funções de dados públicos
from .public_data import (
    get_dados_publicos_processados,
    get_dados_publicos_filtrados,
    get_evolucao_modalidades_mensal
)

# Importar funções de inadimplentes
from .inadimplentes_data import (
    get_inadimplentes_parceiro,
    get_inadimplentes_filtrados
)

# Definir todas as funções disponíveis para importação
__all__ = [
    # API Google Sheets
    'fetch_google_sheet_data',
    'fetch_parceiros_data',
    'fetch_vendas_publicas',

    # Dados de parceiros
    'get_parceiro_vendas_data',
    'get_parceiro_vendas_detalhadas',
    'get_modalidades_parceiro_filtradas',
    'get_cursos_parceiro_filtrados',
    'get_lista_modalidades_parceiro',
    'get_modalidades_parceiro',
    'get_cursos_parceiro',
    'get_modalidades_parceiro_unica',

    # Evolução
    'get_evolucao_matriculas_parceiro',

    # Estatísticas
    'get_estatisticas_parceiro',
    'get_estatisticas_parceiro_filtradas',

    # Dados públicos
    'get_dados_publicos_processados',
    'get_dados_publicos_filtrados',
    'get_evolucao_modalidades_mensal',

    # Inadimplentes
    'get_inadimplentes_parceiro',
    'get_inadimplentes_filtrados'
]
