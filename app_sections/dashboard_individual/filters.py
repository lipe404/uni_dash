# Filtros e Controles
import streamlit as st
from datetime import datetime
from typing import Tuple, Optional, List


def render_evolution_filters() -> Tuple[Optional[int], int]:
    """
    Renderiza filtros para evolução de matrículas
    Returns: (ano_selecionado, mes_selecionado)
    """
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

    with col_filtro1:
        anos_disponiveis = [2024, 2025]
        ano_selecionado = st.selectbox(
            "📅 Selecione o Ano:",
            options=[None] + anos_disponiveis,
            format_func=lambda x: "Todos os anos" if x is None else str(x),
            index=2
        )

    with col_filtro2:
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        mes_atual = datetime.now().month
        meses_opcoes = list(meses.keys())

        try:
            indice_mes_atual = meses_opcoes.index(mes_atual)
        except ValueError:
            indice_mes_atual = 0

        mes_selecionado = st.selectbox(
            "📅 Selecione o Mês:",
            options=meses_opcoes,
            format_func=lambda x: meses[x],
            index=indice_mes_atual
        )

    with col_filtro3:
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()

    return ano_selecionado, mes_selecionado


def render_analysis_filters(modalidades_disponiveis: List[str]) -> Tuple[
        Optional[int], Optional[int], str, str]:
    """
    Renderiza filtros para análise avançada
    Returns: (ano_analise, mes_analise, modalidade_selecionada, tipo_analise)
    """
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    col_filtro_analise1, col_filtro_analise2, col_filtro_analise3, col_filtro_analise4 = st.columns(
        4)

    with col_filtro_analise1:
        ano_analise = st.selectbox(
            "📅 Ano para Análise:",
            options=[2025, 2024, None],
            format_func=lambda x: "Todos os anos" if x is None else str(x),
            index=0,
            key="ano_analise"
        )

    with col_filtro_analise2:
        mes_analise = st.selectbox(
            "📅 Mês para Análise:",
            options=[None] + list(meses.keys()),
            format_func=lambda x: "Todos os meses" if x is None else meses[x],
            index=0,
            key="mes_analise"
        )

    with col_filtro_analise3:
        modalidade_selecionada = st.selectbox(
            "🎯 Modalidade:",
            options=["Todas"] + modalidades_disponiveis,
            index=0,
            key="modalidade_analise"
        )

    with col_filtro_analise4:
        tipo_analise = st.selectbox(
            "📊 Tipo de Análise:",
            options=["Visão Geral", "Comparativo 2025 vs Mês",
                     "Cursos por Modalidade"],
            index=0,
            key="tipo_analise"
        )

    return ano_analise, mes_analise, modalidade_selecionada, tipo_analise


def get_period_text(ano_analise: Optional[int],
                    mes_analise: Optional[int],
                    modalidade_selecionada: str) -> str:
    """
    Gera texto descritivo do período selecionado
    """
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    if ano_analise and mes_analise:
        periodo_texto = f"{meses[mes_analise]} de {ano_analise}"
    elif ano_analise:
        periodo_texto = f"Ano {ano_analise}"
    elif mes_analise:
        periodo_texto = f"{meses[mes_analise]} (todos os anos)"
    else:
        periodo_texto = "Todo o período"

    if modalidade_selecionada and modalidade_selecionada != "Todas":
        periodo_texto += f" - {modalidade_selecionada}"

    return periodo_texto
