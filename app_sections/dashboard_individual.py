import streamlit as st
import plotly.express as px
from data.fetch_data import (
    get_parceiro_vendas_data,
    get_evolucao_matriculas_parceiro,
    get_modalidades_parceiro,
    get_cursos_parceiro
)
from utils.graphs import (
    create_vendas_mensais_chart,
    create_vendas_acumuladas_chart,
    create_kpi_cards,
    create_evolucao_matriculas_chart,
    create_modalidades_parceiro_bar_chart,
    create_modalidades_parceiro_pie_chart,
    create_cursos_parceiro_chart
)
from datetime import datetime


def render_dashboard_individual(parceiro_nome: str):
    """
    Renderiza o dashboard individual do parceiro
    """
    st.title(f"📊 Dashboard - {parceiro_nome}")

    # Buscar dados do parceiro
    with st.spinner("Carregando seus dados..."):
        vendas_data = get_parceiro_vendas_data(parceiro_nome)

    if vendas_data:
        # KPIs
        st.markdown("### 📈 Indicadores Principais")
        create_kpi_cards(vendas_data)

        st.markdown("---")

        # Primeira linha de gráficos
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de vendas mensais
            fig_mensal = create_vendas_mensais_chart(
                vendas_data['vendas_mensais'])
            st.plotly_chart(fig_mensal, use_container_width=True)

        with col2:
            # Gráfico de vendas acumuladas
            fig_acumulado = create_vendas_acumuladas_chart(
                vendas_data['vendas_mensais'])
            st.plotly_chart(fig_acumulado, use_container_width=True)

        st.markdown("---")

        # Filtros para evolução de matrículas
        st.markdown("### 📊 Evolução de Matrículas")

        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

        with col_filtro1:
            anos_disponiveis = [2024, 2025]
            ano_selecionado = st.selectbox(
                "📅 Selecione o Ano:",
                options=[None] + anos_disponiveis,
                format_func=lambda x: "Todos os anos" if x is None else str(x),
                index=2  # Default para 2025
            )

        with col_filtro2:
            meses = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            mes_selecionado = st.selectbox(
                "📅 Selecione o Mês:",
                options=[None] + list(meses.keys()),
                format_func=lambda x: "Todos os meses" if x is None else meses[x],
                index=0
            )

        with col_filtro3:
            if st.button("🔄 Atualizar Dados"):
                st.cache_data.clear()

        # Buscar dados de evolução de matrículas
        with st.spinner("Carregando evolução de matrículas..."):
            evolucao_data = get_evolucao_matriculas_parceiro(
                parceiro_nome,
                ano_selecionado,
                mes_selecionado
            )

        if evolucao_data:
            # Gráfico de evolução de matrículas
            fig_evolucao = create_evolucao_matriculas_chart(
                evolucao_data['evolucao_mensal'])
            st.plotly_chart(fig_evolucao, use_container_width=True)

            # KPI de matrículas
            st.metric(
                label="📚 Total de Matrículas no Período",
                value=int(evolucao_data['total_matriculas'])
            )

        st.markdown("---")

        # Segunda linha de gráficos - Modalidades e Cursos
        st.markdown("### 🎯 Análise de Modalidades e Cursos")

        # Buscar dados de modalidades e cursos
        with st.spinner("Carregando dados de modalidades e cursos..."):
            modalidades_data = get_modalidades_parceiro(parceiro_nome)
            cursos_data = get_cursos_parceiro(parceiro_nome)

        # Gráficos de modalidades
        col1, col2 = st.columns(2)

        with col1:
            if modalidades_data:
                fig_modalidades_bar = create_modalidades_parceiro_bar_chart(
                    modalidades_data)
                st.plotly_chart(fig_modalidades_bar, use_container_width=True)

        with col2:
            if modalidades_data:
                fig_modalidades_pie = create_modalidades_parceiro_pie_chart(
                    modalidades_data)
                st.plotly_chart(fig_modalidades_pie, use_container_width=True)

        # Gráfico de cursos
        if cursos_data:
            fig_cursos = create_cursos_parceiro_chart(cursos_data)
            st.plotly_chart(fig_cursos, use_container_width=True)

        st.markdown("---")

        # Detalhes mensais
        st.markdown("### 📅 Detalhamento Mensal")

        vendas_mensais = vendas_data['vendas_mensais']
        meses_df = []

        for mes, valor in vendas_mensais.items():
            mes_nome = mes.split('./')[0].capitalize()
            meses_df.append({
                'Mês': mes_nome,
                'Vendas': valor,
                'Percentual do Total': f"{(valor / vendas_data['total_2025'] * 100):.1f}%" if vendas_data['total_2025'] > 0 else "0%"
            })

        import pandas as pd
        df_meses = pd.DataFrame(meses_df)
        st.dataframe(df_meses, use_container_width=True)

        # Informações do parceiro
        st.markdown("### ℹ️ Informações do Parceiro")
        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Tipo:** {vendas_data['tipo']}")

        with col2:
            st.info(f"**Responsável:** {vendas_data['responsavel']}")

    else:
        st.error("❌ Não foi possível carregar seus dados. Tente novamente.")
        if st.button("🔄 Recarregar"):
            st.cache_data.clear()
            st.rerun()
