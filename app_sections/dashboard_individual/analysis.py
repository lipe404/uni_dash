# Análise Avançada
import streamlit as st
import pandas as pd
from data.fetch_data import (
    get_modalidades_parceiro_filtradas,
    get_cursos_parceiro_filtrados,
    get_modalidades_parceiro_unica
)
from utils.graphs import (
    create_modalidades_parceiro_bar_chart,
    create_modalidades_parceiro_pie_chart,
    create_cursos_parceiro_chart,
    create_modalidades_evolucao_chart,
    create_cursos_modalidade_chart
)
from typing import Dict, Any, Optional


def render_general_analysis(parceiro_nome: str,
                            ano_analise: Optional[int],
                            mes_analise: Optional[int],
                            modalidade_selecionada: str,
                            periodo_texto: str,
                            stats_data: Dict[str, Any]) -> None:
    """
    Renderiza análise geral (visão geral)
    """
    if modalidade_selecionada and modalidade_selecionada != "Todas":
        _render_specific_modality_analysis(parceiro_nome, ano_analise,
                                           mes_analise, modalidade_selecionada,
                                           periodo_texto, stats_data)
    else:
        _render_all_modalities_analysis(
            parceiro_nome, ano_analise, mes_analise, periodo_texto)


def render_comparative_analysis(
        parceiro_nome: str,
        mes_analise: Optional[int],
        modalidade_selecionada: str) -> None:
    """
    Renderiza análise comparativa 2025 vs Mês
    """
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    if modalidade_selecionada and modalidade_selecionada != "Todas":
        modalidades_2025 = get_modalidades_parceiro_unica(
            parceiro_nome, 2025, None, modalidade_selecionada)
        modalidades_mes = get_modalidades_parceiro_unica(
            parceiro_nome, 2025, mes_analise, modalidade_selecionada)

        if modalidades_2025 and modalidades_mes:
            fig_comparativo = create_modalidades_evolucao_chart(
                modalidades_2025, modalidades_mes, meses[mes_analise])
            fig_comparativo.update_layout(
                title=f'📊 {modalidade_selecionada}: Total 2025 vs {
                    meses[mes_analise]}')
            st.plotly_chart(fig_comparativo, use_container_width=True)
        else:
            st.info(
                f"Dados insuficientes para comparativo da modalidade {
                    modalidade_selecionada}")
    else:
        modalidades_2025 = get_modalidades_parceiro_filtradas(
            parceiro_nome, 2025, None)
        modalidades_mes = get_modalidades_parceiro_filtradas(
            parceiro_nome, 2025, mes_analise)

        fig_comparativo = create_modalidades_evolucao_chart(
            modalidades_2025, modalidades_mes, meses[mes_analise])
        st.plotly_chart(fig_comparativo, use_container_width=True)


def render_courses_by_modality_analysis(parceiro_nome: str,
                                        ano_analise: Optional[int],
                                        mes_analise: Optional[int],
                                        modalidade_selecionada: str,
                                        periodo_texto: str) -> None:
    """
    Renderiza análise de cursos por modalidade
    """
    if modalidade_selecionada == "Todas":
        st.warning(
            "Para análise 'Cursos por Modalidade', selecione uma modalidade específica.")
        return

    cursos_modalidade = get_cursos_parceiro_filtrados(
        parceiro_nome, ano_analise, mes_analise, modalidade_selecionada)

    if cursos_modalidade:
        fig_cursos_modalidade = create_cursos_modalidade_chart(
            cursos_modalidade, modalidade_selecionada)
        fig_cursos_modalidade.update_layout(
            title=f'📚 Cursos de {modalidade_selecionada} - {periodo_texto}')
        st.plotly_chart(fig_cursos_modalidade, use_container_width=True)

        # Tabela detalhada dos cursos
        st.markdown("#### 📋 Detalhamento dos Cursos")
        df_cursos_detalhado = pd.DataFrame([
            {
                'Curso': k,
                'Matrículas': v,
                'Percentual': f"{(v/sum(cursos_modalidade.values())*100):.1f}%"
            }
            for k, v in cursos_modalidade.items()
        ]).sort_values('Matrículas', ascending=False)

        st.dataframe(df_cursos_detalhado,
                     use_container_width=True, hide_index=True)
    else:
        st.info(
            f"Nenhum curso encontrado para a modalidade '{modalidade_selecionada}' no período selecionado.")


def _render_specific_modality_analysis(parceiro_nome: str,
                                       ano_analise: Optional[int],
                                       mes_analise: Optional[int],
                                       modalidade_selecionada: str,
                                       periodo_texto: str,
                                       stats_data: Dict[str, Any]) -> None:
    """
    Renderiza análise para modalidade específica
    """
    modalidades_periodo = get_modalidades_parceiro_unica(
        parceiro_nome, ano_analise, mes_analise, modalidade_selecionada)
    cursos_periodo = get_cursos_parceiro_filtrados(
        parceiro_nome, ano_analise, mes_analise, modalidade_selecionada)

    col1, col2 = st.columns(2)

    with col1:
        if modalidades_periodo:
            fig_modalidades = create_modalidades_parceiro_bar_chart(
                modalidades_periodo)
            fig_modalidades.update_layout(
                title=f'🎯 Modalidade: {modalidade_selecionada} - {periodo_texto}')
            st.plotly_chart(fig_modalidades, use_container_width=True)

    with col2:
        if modalidades_periodo:
            fig_modalidades_pie = create_modalidades_parceiro_pie_chart(
                modalidades_periodo)
            fig_modalidades_pie.update_layout(
                title=f'🥧 {modalidade_selecionada} - {periodo_texto}')
            st.plotly_chart(fig_modalidades_pie, use_container_width=True)

    if cursos_periodo:
        fig_cursos = create_cursos_modalidade_chart(
            cursos_periodo, modalidade_selecionada)
        fig_cursos.update_layout(
            title=f'📚 Cursos de {modalidade_selecionada} - {periodo_texto}')
        st.plotly_chart(fig_cursos, use_container_width=True)

    # Informações específicas da modalidade
    st.markdown("#### 📋 Resumo da Modalidade")
    col_resumo1, col_resumo2, col_resumo3 = st.columns(3)

    with col_resumo1:
        st.info(f"**📚 Total de Matrículas:** {stats_data['total_matriculas']}")

    with col_resumo2:
        st.info(f"**🛒 Total de Vendas:** {stats_data['total_vendas']}")

    with col_resumo3:
        st.info(f"**📖 Cursos Diferentes:** {stats_data['variedade_cursos']}")


def _render_all_modalities_analysis(parceiro_nome: str,
                                    ano_analise: Optional[int],
                                    mes_analise: Optional[int],
                                    periodo_texto: str) -> None:
    """
    Renderiza análise para todas as modalidades
    """
    modalidades_periodo = get_modalidades_parceiro_filtradas(
        parceiro_nome, ano_analise, mes_analise)
    cursos_periodo = get_cursos_parceiro_filtrados(
        parceiro_nome, ano_analise, mes_analise)

    col1, col2 = st.columns(2)

    with col1:
        if modalidades_periodo:
            fig_modalidades = create_modalidades_parceiro_bar_chart(
                modalidades_periodo)
            fig_modalidades.update_layout(
                title=f'🎯 Modalidades - {periodo_texto}')
            st.plotly_chart(fig_modalidades, use_container_width=True)

    with col2:
        if modalidades_periodo:
            fig_modalidades_pie = create_modalidades_parceiro_pie_chart(
                modalidades_periodo)
            fig_modalidades_pie.update_layout(
                title=f'🥧 Distribuição - {periodo_texto}')
            st.plotly_chart(fig_modalidades_pie, use_container_width=True)

    if cursos_periodo:
        fig_cursos = create_cursos_parceiro_chart(cursos_periodo)
        fig_cursos.update_layout(title=f'🏆 Cursos - {periodo_texto}')
        st.plotly_chart(fig_cursos, use_container_width=True)
