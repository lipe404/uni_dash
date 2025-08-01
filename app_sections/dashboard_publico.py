import streamlit as st
from data.fetch_data import get_dados_publicos_processados
from utils.graphs import create_modalidades_chart_percentual, create_cursos_chart_percentual


def render_dashboard_publico():
    """
    Renderiza o dashboard público com dados gerais
    """
    st.title("🌍 Dashboard Público - Dados Gerais")
    st.markdown(
        "*Visualização geral de vendas por modalidades e cursos (apenas porcentagens)*")

    # Buscar dados públicos
    with st.spinner("Carregando dados públicos..."):
        dados_publicos = get_dados_publicos_processados()

    if dados_publicos:
        # KPI geral (removido total de vendas)
        st.markdown("### 📊 Indicadores Gerais")

        # Gráficos com porcentagens
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de modalidades (apenas porcentagens)
            if dados_publicos['modalidades']:
                fig_modalidades = create_modalidades_chart_percentual(
                    dados_publicos['modalidades'])
                st.plotly_chart(fig_modalidades, use_container_width=True)
            else:
                st.warning("Nenhum dado de modalidades encontrado.")

        with col2:
            # Gráfico de cursos (apenas porcentagens)
            if dados_publicos['cursos']:
                fig_cursos = create_cursos_chart_percentual(
                    dados_publicos['cursos'])
                st.plotly_chart(fig_cursos, use_container_width=True)
            else:
                st.warning("Nenhum dado de cursos encontrado.")

        # Tabelas detalhadas (apenas porcentagens)
        st.markdown("### 📋 Detalhamento dos Dados (Distribuição Percentual)")

        tab1, tab2 = st.tabs(["🎯 Modalidades", "📚 Cursos"])

        with tab1:
            if dados_publicos['modalidades']:
                import pandas as pd

                total_modalidades = sum(dados_publicos['modalidades'].values())

                df_modalidades = pd.DataFrame([
                    {
                        'Modalidade': k,
                        'Percentual': f"{(v/total_modalidades*100):.2f}%"
                    }
                    for k, v in dados_publicos['modalidades'].items()
                ]).sort_values('Percentual', key=lambda x: x.str.rstrip('%').astype(float), ascending=False)

                st.dataframe(df_modalidades,
                             use_container_width=True, hide_index=True)

                # Informação adicional
                st.info(
                    f"📊 **Total de modalidades:** {len(dados_publicos['modalidades'])}")

        with tab2:
            if dados_publicos['cursos']:
                import pandas as pd

                total_cursos = sum(dados_publicos['cursos'].values())

                # Mostrar top 15 cursos
                top_cursos = dict(list(dados_publicos['cursos'].items())[:15])

                df_cursos = pd.DataFrame([
                    {
                        'Curso': k,
                        'Percentual': f"{(v/total_cursos*100):.2f}%"
                    }
                    for k, v in top_cursos.items()
                ]).sort_values('Percentual', key=lambda x: x.str.rstrip('%').astype(float), ascending=False)

                st.dataframe(df_cursos, use_container_width=True,
                             hide_index=True)

                # Informações adicionais
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.info(
                        f"📚 **Total de cursos diferentes:** {len(dados_publicos['cursos'])}")
                with col_info2:
                    outros_cursos = len(dados_publicos['cursos']) - 15
                    if outros_cursos > 0:
                        st.info(f"➕ **Outros cursos:** {outros_cursos}")

        # Seção de insights
        st.markdown("---")
        st.markdown("### 💡 Insights dos Dados")

        if dados_publicos['modalidades'] and dados_publicos['cursos']:
            col_insight1, col_insight2 = st.columns(2)

            with col_insight1:
                # Modalidade mais popular
                modalidade_top = max(
                    dados_publicos['modalidades'].items(), key=lambda x: x[1])
                total_modalidades = sum(dados_publicos['modalidades'].values())
                percentual_top_modalidade = (
                    modalidade_top[1] / total_modalidades) * 100

                st.success(
                    f"🎯 **Modalidade Líder:** {modalidade_top[0]} ({percentual_top_modalidade:.1f}%)")

            with col_insight2:
                # Curso mais popular
                curso_top = max(
                    dados_publicos['cursos'].items(), key=lambda x: x[1])
                total_cursos = sum(dados_publicos['cursos'].values())
                percentual_top_curso = (curso_top[1] / total_cursos) * 100

                # Limitar nome do curso se muito longo
                curso_nome = curso_top[0][:40] + \
                    "..." if len(curso_top[0]) > 40 else curso_top[0]
                st.success(
                    f"📚 **Curso Líder:** {curso_nome} ({percentual_top_curso:.1f}%)")

    else:
        st.error("❌ Não foi possível carregar os dados públicos. Tente novamente.")
        if st.button("🔄 Recarregar"):
            st.cache_data.clear()
            st.rerun()
