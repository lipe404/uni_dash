import streamlit as st
import plotly.express as px
from data.fetch_data import get_parceiro_vendas_data
from utils.graphs import (
    create_vendas_mensais_chart,
    create_vendas_acumuladas_chart,
    create_kpi_cards
)


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

        # Gráficos
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
            st.rerun()
