import streamlit as st
from data.fetch_data import get_dados_publicos_processados
from utils.graphs import create_modalidades_chart, create_cursos_chart


def render_dashboard_publico():
    """
    Renderiza o dashboard público com dados gerais
    """
    st.title("🌍 Dashboard Público - Dados Gerais")
    st.markdown("*Visualização geral de vendas por modalidades e cursos*")

    # Buscar dados públicos
    with st.spinner("Carregando dados públicos..."):
        dados_publicos = get_dados_publicos_processados()

    if dados_publicos:
        # KPI geral
        st.markdown("### 📊 Indicador Geral")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="📈 Total de Vendas",
                value=dados_publicos['total_vendas'],
                delta=None
            )

        with col2:
            st.metric(
                label="🎯 Modalidades",
                value=len(dados_publicos['modalidades']),
                delta=None
            )

        with col3:
            st.metric(
                label="📚 Cursos Diferentes",
                value=len(dados_publicos['cursos']),
                delta=None
            )

        st.markdown("---")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de modalidades
            if dados_publicos['modalidades']:
                fig_modalidades = create_modalidades_chart(
                    dados_publicos['modalidades'])
                st.plotly_chart(fig_modalidades, use_container_width=True)
            else:
                st.warning("Nenhum dado de modalidades encontrado.")

        with col2:
            # Gráfico de cursos
            if dados_publicos['cursos']:
                fig_cursos = create_cursos_chart(dados_publicos['cursos'])
                st.plotly_chart(fig_cursos, use_container_width=True)
            else:
                st.warning("Nenhum dado de cursos encontrado.")

        # Tabelas detalhadas
        st.markdown("### 📋 Detalhamento dos Dados")

        tab1, tab2 = st.tabs(["🎯 Modalidades", "📚 Cursos"])

        with tab1:
            if dados_publicos['modalidades']:
                import pandas as pd
                df_modalidades = pd.DataFrame([
                    {'Modalidade': k, 'Vendas': v,
                        'Percentual': f"{(v/dados_publicos['total_vendas']*100):.1f}%"}
                    for k, v in dados_publicos['modalidades'].items()
                ]).sort_values('Vendas', ascending=False)

                st.dataframe(df_modalidades, use_container_width=True)

        with tab2:
            if dados_publicos['cursos']:
                import pandas as pd
                df_cursos = pd.DataFrame([
                    {'Curso': k, 'Vendas': v,
                        'Percentual': f"{(v/dados_publicos['total_vendas']*100):.1f}%"}
                    # Top 15
                    for k, v in list(dados_publicos['cursos'].items())[:15]
                ]).sort_values('Vendas', ascending=False)

                st.dataframe(df_cursos, use_container_width=True)

    else:
        st.error("❌ Não foi possível carregar os dados públicos. Tente novamente.")
        if st.button("🔄 Recarregar"):
            st.rerun()
