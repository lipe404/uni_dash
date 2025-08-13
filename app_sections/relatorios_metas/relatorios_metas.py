# app_sections/relatorios_metas/relatorios_metas.py
import streamlit as st
from typing import List
from data.fetch_data import get_parceiro_vendas_data, get_lista_modalidades_parceiro
from .projections import render_projections_section
from .reports import render_reports_section
from .inadimplentes import render_inadimplentes_section


def render_relatorios_metas(parceiro_nome: str):
    """Renderiza a página de Relatórios e Metas"""

    st.markdown(f"""
    <div class="main-header">
        <h1>📋 Relatórios e Metas</h1>
        <h3>{parceiro_nome}</h3>
        <p>Gere relatórios detalhados e acompanhe projeções de vendas</p>
    </div>
    """, unsafe_allow_html=True)

    # Carregar dados básicos
    with st.spinner("Carregando dados..."):
        vendas_data = get_parceiro_vendas_data(parceiro_nome)
        modalidades_disponiveis = get_lista_modalidades_parceiro(parceiro_nome)

    if not vendas_data:
        st.error("❌ Não foi possível carregar os dados. Tente novamente.")
        return

    # Criar tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Projeções e Metas",
        "📄 Geração de Relatórios",
        "⚠️ Relatório de Inadimplentes"
    ])

    with tab1:
        render_projections_section(vendas_data, parceiro_nome)

    with tab2:
        render_reports_section(parceiro_nome, modalidades_disponiveis)

    with tab3:
        render_inadimplentes_section(parceiro_nome, modalidades_disponiveis)
