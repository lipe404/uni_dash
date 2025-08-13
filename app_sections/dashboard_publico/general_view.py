# app_sections/dashboard_publico/general_view.py
import streamlit as st
from data.fetch_data import get_dados_publicos_processados
from .components import render_tabelas_detalhadas, render_insights, render_charts_section


def render_visao_geral() -> None:
    """
    Renderiza a visão geral dos dados
    """
    with st.spinner("Carregando dados gerais..."):
        dados_publicos = get_dados_publicos_processados()

    if dados_publicos:
        # Gráficos com porcentagens
        render_charts_section(dados_publicos)

        # Tabelas detalhadas
        render_tabelas_detalhadas(dados_publicos)
        render_insights(dados_publicos)

    else:
        st.error("❌ Não foi possível carregar os dados públicos.")
