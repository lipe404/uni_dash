# Detalhes e Informações
import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_monthly_details(vendas_data: Dict[str, Any]) -> None:
    """
    Renderiza detalhamento mensal
    """
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

    df_meses = pd.DataFrame(meses_df)
    st.dataframe(df_meses, use_container_width=True)


def render_partner_info(vendas_data: Dict[str, Any]) -> None:
    """
    Renderiza informações do parceiro
    """
    st.markdown("### ℹ️ Informações do Parceiro")
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Tipo:** {vendas_data['tipo']}")

    with col2:
        st.info(f"**Responsável:** {vendas_data['responsavel']}")


def render_error_state() -> None:
    """
    Renderiza estado de erro
    """
    st.error("❌ Não foi possível carregar seus dados. Tente novamente.")
    if st.button("🔄 Recarregar"):
        st.cache_data.clear()
        st.rerun()
