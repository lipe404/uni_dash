# app_sections/dashboard_publico/period_comparison.py
import streamlit as st
import pandas as pd
from data.fetch_data import get_dados_publicos_processados, get_dados_publicos_filtrados
from utils.graphs import create_modalidades_comparativo_chart


def render_comparativo_periodo() -> None:
    """
    Renderiza comparativo entre diferentes períodos
    """
    with st.spinner("Carregando dados para comparativo..."):
        dados_geral = get_dados_publicos_processados()
        dados_2024 = get_dados_publicos_filtrados(2024)
        dados_2025 = get_dados_publicos_filtrados(2025)

    # Verificar se temos dados para comparar
    tem_dados = any([
        dados_geral and dados_geral.get('modalidades'),
        dados_2024 and dados_2024.get('modalidades'),
        dados_2025 and dados_2025.get('modalidades')
    ])

    if tem_dados:
        st.markdown("### 📊 Comparativo de Modalidades por Período")

        # Preparar dados para gráfico
        modalidades_geral = dados_geral.get(
            'modalidades', {}) if dados_geral else {}
        modalidades_2024 = dados_2024.get(
            'modalidades', {}) if dados_2024 else {}
        modalidades_2025 = dados_2025.get(
            'modalidades', {}) if dados_2025 else {}

        # Gráfico comparativo
        fig_comparativo = create_modalidades_comparativo_chart(
            modalidades_2024, modalidades_2025, modalidades_geral
        )
        st.plotly_chart(fig_comparativo, use_container_width=True)

        # Tabela comparativa
        _render_comparative_table(
            modalidades_geral, modalidades_2024, modalidades_2025)

        # Insights comparativos
        _render_comparative_insights(
            modalidades_geral, modalidades_2024, modalidades_2025)

    else:
        st.error("❌ Não foi possível carregar dados para comparativo.")


def _render_comparative_table(modalidades_geral: dict, modalidades_2024: dict, modalidades_2025: dict) -> None:
    """
    Renderiza tabela comparativa
    """
    st.markdown("#### 📋 Tabela Comparativa")

    # Combinar todas as modalidades
    todas_modalidades = set()
    if modalidades_geral:
        todas_modalidades.update(modalidades_geral.keys())
    if modalidades_2024:
        todas_modalidades.update(modalidades_2024.keys())
    if modalidades_2025:
        todas_modalidades.update(modalidades_2025.keys())

    # Calcular totais para porcentagens
    total_geral = sum(modalidades_geral.values()) if modalidades_geral else 0
    total_2024 = sum(modalidades_2024.values()) if modalidades_2024 else 0
    total_2025 = sum(modalidades_2025.values()) if modalidades_2025 else 0

    dados_comparativo = []
    for modalidade in sorted(todas_modalidades):
        linha = {'Modalidade': modalidade}

        if modalidades_geral:
            perc_geral = (modalidades_geral.get(modalidade, 0) /
                          total_geral * 100) if total_geral > 0 else 0
            linha['Geral (%)'] = f"{perc_geral:.1f}%"

        if modalidades_2024:
            perc_2024 = (modalidades_2024.get(modalidade, 0) /
                         total_2024 * 100) if total_2024 > 0 else 0
            linha['2024 (%)'] = f"{perc_2024:.1f}%"

        if modalidades_2025:
            perc_2025 = (modalidades_2025.get(modalidade, 0) /
                         total_2025 * 100) if total_2025 > 0 else 0
            linha['2025 (%)'] = f"{perc_2025:.1f}%"

        dados_comparativo.append(linha)

    if dados_comparativo:
        df_comparativo = pd.DataFrame(dados_comparativo)
        st.dataframe(df_comparativo, use_container_width=True, hide_index=True)


def _render_comparative_insights(modalidades_geral: dict, modalidades_2024: dict, modalidades_2025: dict) -> None:
    """
    Renderiza insights comparativos
    """
    st.markdown("#### 💡 Insights Comparativos")

    col_comp1, col_comp2, col_comp3 = st.columns(3)

    # Calcular totais
    total_geral = sum(modalidades_geral.values()) if modalidades_geral else 0
    total_2024 = sum(modalidades_2024.values()) if modalidades_2024 else 0
    total_2025 = sum(modalidades_2025.values()) if modalidades_2025 else 0

    if modalidades_geral:
        with col_comp1:
            top_geral = max(modalidades_geral.items(), key=lambda x: x[1])
            perc_geral = (top_geral[1] / total_geral *
                          100) if total_geral > 0 else 0
            st.success(f"🏆 **Geral:** {top_geral[0]} ({perc_geral:.1f}%)")

    if modalidades_2024:
        with col_comp2:
            top_2024 = max(modalidades_2024.items(), key=lambda x: x[1])
            perc_2024 = (top_2024[1] / total_2024 *
                         100) if total_2024 > 0 else 0
            st.info(f"📅 **2024:** {top_2024[0]} ({perc_2024:.1f}%)")

    if modalidades_2025:
        with col_comp3:
            top_2025 = max(modalidades_2025.items(), key=lambda x: x[1])
            perc_2025 = (top_2025[1] / total_2025 *
                         100) if total_2025 > 0 else 0
            st.warning(f"🆕 **2025:** {top_2025[0]} ({perc_2025:.1f}%)")
