# app_sections/dashboard_publico/components.py
import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_tabelas_detalhadas(dados_publicos: Dict[str, Any],
                              periodo_texto: str = "") -> None:
    """
    Renderiza tabelas detalhadas dos dados
    """
    titulo = f" Detalhamento dos Dados{' - ' + periodo_texto if periodo_texto else ''}"
    st.markdown(f"### {titulo}")

    tab1, tab2 = st.tabs(["🎯 Modalidades", "📚 Cursos"])

    with tab1:
        if dados_publicos['modalidades']:
            total_modalidades = sum(dados_publicos['modalidades'].values())

            df_modalidades = pd.DataFrame([
                {
                    'Modalidade': k,
                    'Percentual': f"{(v/total_modalidades*100):.2f}%"
                }
                for k, v in dados_publicos['modalidades'].items()
            ]).sort_values('Percentual', key=lambda x: x.str.rstrip(
                '%').astype(float), ascending=False)

            st.dataframe(df_modalidades, use_container_width=True,
                         hide_index=True)
            st.info(
                f"📊 **Total de modalidades:** {len(dados_publicos['modalidades'])}")

    with tab2:
        if dados_publicos['cursos']:
            total_cursos = sum(dados_publicos['cursos'].values())
            top_cursos = dict(list(dados_publicos['cursos'].items())[:15])

            df_cursos = pd.DataFrame([
                {
                    'Curso': k,
                    'Percentual': f"{(v/total_cursos*100):.2f}%"
                }
                for k, v in top_cursos.items()
            ]).sort_values('Percentual', key=lambda x: x.str.rstrip(
                '%').astype(float), ascending=False)

            st.dataframe(df_cursos, use_container_width=True, hide_index=True)

            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(
                    f"📚 **Total de cursos diferentes:** {len(dados_publicos['cursos'])}")
            with col_info2:
                outros_cursos = len(dados_publicos['cursos']) - 15
                if outros_cursos > 0:
                    st.info(f"➕ **Outros cursos:** {outros_cursos}")


def render_insights(dados_publicos: Dict[str, Any],
                    periodo_texto: str = "") -> None:
    """
    Renderiza insights dos dados
    """
    st.markdown("---")
    titulo = f"💡 Insights dos Dados{' - ' + periodo_texto if periodo_texto else ''}"
    st.markdown(f"### {titulo}")

    if dados_publicos['modalidades'] and dados_publicos['cursos']:
        col_insight1, col_insight2 = st.columns(2)

        with col_insight1:
            modalidade_top = max(
                dados_publicos['modalidades'].items(), key=lambda x: x[1])
            total_modalidades = sum(dados_publicos['modalidades'].values())
            percentual_top_modalidade = (
                modalidade_top[1] / total_modalidades) * 100

            st.success(
                f"🎯 **Modalidade Líder:** {modalidade_top[0]} ({percentual_top_modalidade:.1f}%)")

        with col_insight2:
            curso_top = max(
                dados_publicos['cursos'].items(), key=lambda x: x[1])
            total_cursos = sum(dados_publicos['cursos'].values())
            percentual_top_curso = (curso_top[1] / total_cursos) * 100

            curso_nome = curso_top[0][:40] + \
                "..." if len(curso_top[0]) > 40 else curso_top[0]
            st.success(
                f"📚 **Curso Líder:** {curso_nome} ({percentual_top_curso:.1f}%)")


def render_charts_section(dados: Dict[str, Any],
                          periodo_texto: str = "") -> None:
    """
    Renderiza seção de gráficos
    """
    from utils.graphs import create_modalidades_chart_percentual, create_cursos_chart_percentual

    col1, col2 = st.columns(2)

    with col1:
        if dados['modalidades']:
            fig_modalidades = create_modalidades_chart_percentual(
                dados['modalidades'])
            if periodo_texto:
                fig_modalidades.update_layout(
                    title=f'🎯 Modalidades - {periodo_texto}')
            st.plotly_chart(fig_modalidades, use_container_width=True)
        else:
            st.warning("Nenhum dado de modalidades encontrado.")

    with col2:
        if dados['cursos']:
            fig_cursos = create_cursos_chart_percentual(dados['cursos'])
            if periodo_texto:
                fig_cursos.update_layout(title=f'📚 Cursos - {periodo_texto}')
            st.plotly_chart(fig_cursos, use_container_width=True)
        else:
            st.warning("Nenhum dado de cursos encontrado.")
