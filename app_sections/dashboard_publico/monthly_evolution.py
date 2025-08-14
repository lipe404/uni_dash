# app_sections/dashboard_publico/monthly_evolution.py
import streamlit as st
import pandas as pd
from data.fetch_data import get_evolucao_modalidades_mensal
from utils.graphs import create_evolucao_modalidades_linha_chart


def render_evolucao_mensal(ano_evolucao: int) -> None:
    """
    Renderiza gráfico de evolução mensal
    """
    with st.spinner(f"Carregando evolução mensal de {ano_evolucao}..."):
        evolucao_data = get_evolucao_modalidades_mensal(ano_evolucao)

    if evolucao_data:
        st.markdown(f"### 📈 Evolução das Modalidades - {ano_evolucao}")

        # Gráfico de linha da evolução
        fig_evolucao = create_evolucao_modalidades_linha_chart(evolucao_data)
        st.plotly_chart(fig_evolucao, use_container_width=True)

        # Tabela de dados mensais
        _render_monthly_data_table(evolucao_data)

        # Insights da evolução
        _render_evolution_insights(evolucao_data)

    else:
        st.info(f"Nenhum dado de evolução encontrado para {ano_evolucao}")


def _render_monthly_data_table(evolucao_data: dict) -> None:
    """
    Renderiza tabela de dados mensais detalhados
    """
    st.markdown("#### 📋 Dados Mensais Detalhados")

    # Preparar dados para tabela
    dados_tabela = []
    for mes, dados_mes in evolucao_data.items():
        if dados_mes['modalidades']:
            modalidade_principal = max(
                dados_mes['modalidades'].items(), key=lambda x: x[1])
            dados_tabela.append({
                'Mês': mes,
                'Modalidade Principal': modalidade_principal[0],
                'Percentual Principal': f"{modalidade_principal[1]:.1f}%",
                'Modalidades Diferentes': len(dados_mes['modalidades'])
            })

    if dados_tabela:
        df_evolucao = pd.DataFrame(dados_tabela)
        st.dataframe(df_evolucao, use_container_width=True, hide_index=True)


def _render_evolution_insights(evolucao_data: dict) -> None:
    """
    Renderiza insights da evolução
    """
    st.markdown("#### Insights da Evolução")

    if len(evolucao_data) >= 2:
        # Comparar primeiro e último mês com dados
        meses_com_dados = [
            mes for mes, dados in evolucao_data.items() if dados[
                'modalidades']]

        if len(meses_com_dados) >= 2:
            primeiro_mes = meses_com_dados[0]
            ultimo_mes = meses_com_dados[-1]

            modalidade_inicio = max(
                evolucao_data[primeiro_mes][
                    'modalidades'].items(), key=lambda x: x[1])
            modalidade_fim = max(
                evolucao_data[ultimo_mes][
                    'modalidades'].items(), key=lambda x: x[1])

            col_insight1, col_insight2 = st.columns(2)

            with col_insight1:
                st.info(
                    f"🚀 **{primeiro_mes}:** {modalidade_inicio[0]} ({modalidade_inicio[1]:.1f}%)")

            with col_insight2:
                st.info(
                    f"🏁 **{ultimo_mes}:** {modalidade_fim[0]} ({modalidade_fim[1]:.1f}%)")
