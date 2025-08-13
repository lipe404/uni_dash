# app_sections/dashboard_publico/dashboard_publico.py
import streamlit as st
from .filters import render_analysis_filters, get_period_description
from .general_view import render_visao_geral
from .filtered_analysis import render_analise_filtrada
from .monthly_evolution import render_evolucao_mensal
from .period_comparison import render_comparativo_periodo


def render_dashboard_publico():
    """
    Renderiza o dashboard público com dados gerais
    """
    st.title("🌍 Dashboard Público - Dados Gerais")
    st.markdown("*Visualização geral de vendas por modalidades e cursos*")

    # Seção de filtros
    st.markdown("### 🔍 Filtros de Análise")

    tipo_analise, ano_filtro, mes_filtro, ano_evolucao = render_analysis_filters()

    # Definir período para exibição
    periodo_texto = get_period_description(
        tipo_analise, ano_filtro, mes_filtro, ano_evolucao)

    st.markdown(f"**📊 Período analisado:** {periodo_texto}")
    st.markdown("---")

    # Renderizar conteúdo baseado no tipo de análise
    if tipo_analise == "Visão Geral":
        render_visao_geral()

    elif tipo_analise == "Análise Filtrada":
        render_analise_filtrada(ano_filtro, mes_filtro, periodo_texto)

    elif tipo_analise == "Evolução Mensal":
        render_evolucao_mensal(ano_evolucao)

    elif tipo_analise == "Comparativo por Período":
        render_comparativo_periodo()
