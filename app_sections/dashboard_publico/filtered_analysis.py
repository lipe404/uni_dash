# app_sections/dashboard_publico/filtered_analysis.py
import streamlit as st
from typing import Optional
from data.fetch_data import get_dados_publicos_filtrados
from .components import render_tabelas_detalhadas, render_insights, render_charts_section


def render_analise_filtrada(ano_filtro: Optional[int],
                            mes_filtro: Optional[int],
                            periodo_texto: str) -> None:
    """
    Renderiza análise com filtros específicos
    """
    with st.spinner("Carregando dados filtrados..."):
        dados_filtrados = get_dados_publicos_filtrados(ano_filtro, mes_filtro)

    if dados_filtrados:
        # KPI do período filtrado
        st.markdown("### 📊 Indicadores do Período")

        # Gráficos filtrados
        render_charts_section(dados_filtrados, periodo_texto)

        # Tabelas do período filtrado
        render_tabelas_detalhadas(dados_filtrados, periodo_texto)
        render_insights(dados_filtrados, periodo_texto)

    else:
        st.info(f"Nenhum dado encontrado para o período: {periodo_texto}")
