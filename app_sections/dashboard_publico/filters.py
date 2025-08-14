# app_sections/dashboard_publico/filters.py
import streamlit as st
from typing import Tuple, Optional


def render_analysis_filters() -> Tuple[str, Optional[int], Optional[int], int]:
    """
    Renderiza filtros de análise do dashboard público
    Returns: (tipo_analise, ano_filtro, mes_filtro, ano_evolucao)
    """
    col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)

    with col_filtro1:
        tipo_analise = st.selectbox(
            "📊 Tipo de Análise:",
            options=["Visão Geral", "Análise Filtrada",
                     "Evolução Mensal", "Comparativo por Período"],
            index=0
        )

    with col_filtro2:
        if tipo_analise in ["Análise Filtrada", "Comparativo por Período"]:
            ano_filtro = st.selectbox(
                "📅 Ano:",
                options=[None, 2024, 2025],
                format_func=lambda x: "Todos os anos" if x is None else str(x),
                index=0
            )
        else:
            ano_filtro = None

    with col_filtro3:
        if tipo_analise == "Análise Filtrada":
            meses = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            mes_filtro = st.selectbox(
                "📅 Mês:",
                options=[None] + list(meses.keys()),
                format_func=lambda x: "Todos os meses" if x is None else meses[x],
                index=0
            )
        else:
            mes_filtro = None

    with col_filtro4:
        if tipo_analise == "Evolução Mensal":
            ano_evolucao = st.selectbox(
                "📅 Ano para Evolução:",
                options=[2024, 2025],
                index=1
            )
        else:
            ano_evolucao = 2025

    return tipo_analise, ano_filtro, mes_filtro, ano_evolucao


def get_period_description(tipo_analise: str,
                           ano_filtro: Optional[int],
                           mes_filtro: Optional[int],
                           ano_evolucao: int) -> str:
    """
    Gera descrição do período baseado nos filtros
    """
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    if tipo_analise == "Análise Filtrada":
        if ano_filtro and mes_filtro:
            return f"{meses[mes_filtro]} de {ano_filtro}"
        elif ano_filtro:
            return f"Ano {ano_filtro}"
        elif mes_filtro:
            return f"{meses[mes_filtro]} (todos os anos)"
        else:
            return "Todo o período"
    elif tipo_analise == "Evolução Mensal":
        return f"Evolução mensal - {ano_evolucao}"
    elif tipo_analise == "Comparativo por Período":
        return "Comparativo entre períodos"
    else:
        return "Dados gerais"
