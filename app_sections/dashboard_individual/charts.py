# Gráficos Principais
import streamlit as st
from utils.graphs import (
    create_vendas_mensais_chart,
    create_vendas_acumuladas_chart,
    create_evolucao_matriculas_chart
)
from typing import Dict, Any, List


def render_main_charts(vendas_data: Dict[str, Any]) -> None:
    """
    Renderiza os gráficos principais do dashboard
    """
    col1, col2 = st.columns(2)

    with col1:
        fig_mensal = create_vendas_mensais_chart(vendas_data['vendas_mensais'])
        st.plotly_chart(fig_mensal, use_container_width=True)

    with col2:
        fig_acumulado = create_vendas_acumuladas_chart(
            vendas_data['vendas_mensais'])
        st.plotly_chart(fig_acumulado, use_container_width=True)


def render_evolution_chart(evolucao_data: List[Dict[str, Any]],
                           mes_nome: str, ano: int) -> None:
    """
    Renderiza gráfico de evolução de matrículas
    """
    fig_evolucao = create_evolucao_matriculas_chart(evolucao_data)
    st.plotly_chart(fig_evolucao, use_container_width=True)


def render_no_evolution_data(mes_nome: str, ano_selecionado: int) -> None:
    """
    Renderiza mensagem quando não há dados de evolução
    """
    st.info(
        f"Nenhuma matrícula encontrada para {mes_nome} de {ano_selecionado if ano_selecionado else 'todos os anos'}."
    )
