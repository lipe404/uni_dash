# Métricas e Indicadores
import streamlit as st
from utils.graphs import create_kpi_cards, create_kpi_analise_cards
from typing import Dict, Any


def render_main_kpis(vendas_data: Dict[str, Any]) -> None:
    """
    Renderiza os KPIs principais do dashboard
    """
    st.markdown("### 📈 Indicadores Principais")
    create_kpi_cards(vendas_data)


def render_analysis_kpis(stats_data: Dict[str, Any], periodo_texto: str) -> None:
    """
    Renderiza os KPIs da análise avançada
    """
    st.markdown("#### 📊 Indicadores do Período")
    create_kpi_analise_cards(stats_data, periodo_texto)


def render_evolution_metric(evolucao_result: Dict[str, Any]) -> None:
    """
    Renderiza métrica de evolução de matrículas
    """
    st.metric(
        label="📚 Total de Matrículas no Período",
        value=int(evolucao_result['total_matriculas'])
    )


def render_highlights(stats_data: Dict[str, Any], modalidade_selecionada: str) -> None:
    """
    Renderiza destaques do período
    """
    st.markdown("#### 🏆 Destaques do Período")
    col_destaque1, col_destaque2 = st.columns(2)

    with col_destaque1:
        modalidade_top = stats_data.get('modalidade_top', ('Nenhuma', 0))
        if modalidade_selecionada and modalidade_selecionada != "Todas":
            st.success(
                f"**🎯 Modalidade Analisada:** {modalidade_top[0]} ({modalidade_top[1]} matrículas)")
        else:
            st.success(
                f"**🎯 Modalidade Mais Vendida:** {modalidade_top[0]} ({modalidade_top[1]} vendas)")

    with col_destaque2:
        curso_top = stats_data.get('curso_top', ('Nenhum', 0))
        curso_nome = curso_top[0][:50] + \
            "..." if len(curso_top[0]) > 50 else curso_top[0]
        if modalidade_selecionada and modalidade_selecionada != "Todas":
            st.success(
                f"**📚 Curso Mais Vendido em {modalidade_selecionada}:** {curso_nome} ({curso_top[1]} vendas)")
        else:
            st.success(
                f"**📚 Curso Mais Vendido:** {curso_nome} ({curso_top[1]} vendas)")
