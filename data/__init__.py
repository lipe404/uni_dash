# data/__init__.py
from .fetch_data import *

__all__ = [
    'fetch_google_sheet_data',
    'fetch_parceiros_data',
    'fetch_vendas_publicas',
    'get_parceiro_vendas_data',
    'get_parceiro_vendas_detalhadas',
    'get_evolucao_matriculas_parceiro',
    'get_modalidades_parceiro_filtradas',
    'get_cursos_parceiro_filtrados',
    'get_lista_modalidades_parceiro',
    'get_estatisticas_parceiro',
    'get_modalidades_parceiro',
    'get_cursos_parceiro',
    'get_estatisticas_parceiro_filtradas',
    'get_modalidades_parceiro_unica',
    'get_dados_publicos_processados',
    'get_dados_publicos_filtrados',
    'get_evolucao_modalidades_mensal',
    'get_inadimplentes_parceiro',
    'get_inadimplentes_filtrados'
]
