import streamlit as st
from data.fetch_data import (
    get_dados_publicos_processados,
    get_dados_publicos_filtrados,
    get_evolucao_modalidades_mensal
)
from utils.graphs import (
    create_modalidades_chart_percentual,
    create_cursos_chart_percentual,
    create_evolucao_modalidades_linha_chart,
    create_modalidades_comparativo_chart
)
from datetime import datetime


def render_dashboard_publico():
    """
    Renderiza o dashboard público com dados gerais
    """
    st.title("🌍 Dashboard Público - Dados Gerais")
    st.markdown("*Visualização geral de vendas por modalidades e cursos*")

    # Seção de filtros
    st.markdown("### 🔍 Filtros de Análise")

    col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)

    with col_filtro1:
        tipo_analise = st.selectbox(
            "📊 Tipo de Análise:",
            options=["Visão Geral", "Análise Filtrada",
                     "Evolução Mensal", "Comparativo por Período"],
            index=0
        )

    with col_filtro2:
        if tipo_analise in ["Análise Filtrada", "Comparativo por Período"]:
            ano_filtro = st.selectbox(
                "📅 Ano:",
                options=[None, 2024, 2025],
                format_func=lambda x: "Todos os anos" if x is None else str(x),
                index=0
            )
        else:
            ano_filtro = None

    with col_filtro3:
        if tipo_analise == "Análise Filtrada":
            meses = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            mes_filtro = st.selectbox(
                "📅 Mês:",
                options=[None] + list(meses.keys()),
                format_func=lambda x: "Todos os meses" if x is None else meses[x],
                index=0
            )
        else:
            mes_filtro = None

    with col_filtro4:
        if tipo_analise == "Evolução Mensal":
            ano_evolucao = st.selectbox(
                "📅 Ano para Evolução:",
                options=[2024, 2025],
                index=1
            )
        else:
            ano_evolucao = 2025

    # Definir período para exibição
    if tipo_analise == "Análise Filtrada":
        if ano_filtro and mes_filtro:
            periodo_texto = f"{meses[mes_filtro]} de {ano_filtro}"
        elif ano_filtro:
            periodo_texto = f"Ano {ano_filtro}"
        elif mes_filtro:
            periodo_texto = f"{meses[mes_filtro]} (todos os anos)"
        else:
            periodo_texto = "Todo o período"
    elif tipo_analise == "Evolução Mensal":
        periodo_texto = f"Evolução mensal - {ano_evolucao}"
    elif tipo_analise == "Comparativo por Período":
        periodo_texto = "Comparativo entre períodos"
    else:
        periodo_texto = "Dados gerais"

    st.markdown(f"**📊 Período analisado:** {periodo_texto}")
    st.markdown("---")

    # Renderizar conteúdo baseado no tipo de análise
    if tipo_analise == "Visão Geral":
        render_visao_geral()

    elif tipo_analise == "Análise Filtrada":
        render_analise_filtrada(ano_filtro, mes_filtro, periodo_texto)

    elif tipo_analise == "Evolução Mensal":
        render_evolucao_mensal(ano_evolucao)

    elif tipo_analise == "Comparativo por Período":
        render_comparativo_periodo()


def render_visao_geral():
    """
    Renderiza a visão geral dos dados
    """
    with st.spinner("Carregando dados gerais..."):
        dados_publicos = get_dados_publicos_processados()

    if dados_publicos:
        # Gráficos com porcentagens
        col1, col2 = st.columns(2)

        with col1:
            if dados_publicos['modalidades']:
                fig_modalidades = create_modalidades_chart_percentual(
                    dados_publicos['modalidades'])
                st.plotly_chart(fig_modalidades, use_container_width=True)
            else:
                st.warning("Nenhum dado de modalidades encontrado.")

        with col2:
            if dados_publicos['cursos']:
                fig_cursos = create_cursos_chart_percentual(
                    dados_publicos['cursos'])
                st.plotly_chart(fig_cursos, use_container_width=True)
            else:
                st.warning("Nenhum dado de cursos encontrado.")

        # Tabelas detalhadas
        render_tabelas_detalhadas(dados_publicos)
        render_insights(dados_publicos)

    else:
        st.error("❌ Não foi possível carregar os dados públicos.")


def render_analise_filtrada(ano_filtro, mes_filtro, periodo_texto):
    """
    Renderiza análise com filtros específicos
    """
    with st.spinner("Carregando dados filtrados..."):
        dados_filtrados = get_dados_publicos_filtrados(ano_filtro, mes_filtro)

    if dados_filtrados:
        # KPI do período filtrado
        st.markdown("### 📊 Indicadores do Período")

        # Gráficos filtrados
        col1, col2 = st.columns(2)

        with col1:
            if dados_filtrados['modalidades']:
                fig_modalidades = create_modalidades_chart_percentual(
                    dados_filtrados['modalidades'])
                fig_modalidades.update_layout(
                    title=f'🎯 Modalidades - {periodo_texto}')
                st.plotly_chart(fig_modalidades, use_container_width=True)

        with col2:
            if dados_filtrados['cursos']:
                fig_cursos = create_cursos_chart_percentual(
                    dados_filtrados['cursos'])
                fig_cursos.update_layout(title=f'📚 Cursos - {periodo_texto}')
                st.plotly_chart(fig_cursos, use_container_width=True)

        # Tabelas do período filtrado
        render_tabelas_detalhadas(dados_filtrados, periodo_texto)
        render_insights(dados_filtrados, periodo_texto)

    else:
        st.info(f"Nenhum dado encontrado para o período: {periodo_texto}")


def render_evolucao_mensal(ano_evolucao):
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
        st.markdown("#### 📋 Dados Mensais Detalhados")

        import pandas as pd

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
            st.dataframe(df_evolucao, use_container_width=True,
                         hide_index=True)

        # Insights da evolução
        st.markdown("#### 💡 Insights da Evolução")

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

    else:
        st.info(f"Nenhum dado de evolução encontrado para {ano_evolucao}")


def render_comparativo_periodo():
    """
    Renderiza comparativo entre diferentes períodos
    """
    with st.spinner("Carregando dados para comparativo..."):
        dados_geral = get_dados_publicos_processados()
        dados_2024 = get_dados_publicos_filtrados(2024)
        dados_2025 = get_dados_publicos_filtrados(2025)

    # Verificar se temos dados para comparar
    tem_dados = any([
        dados_geral and dados_geral.get('modalidades'),
        dados_2024 and dados_2024.get('modalidades'),
        dados_2025 and dados_2025.get('modalidades')
    ])

    if tem_dados:
        st.markdown("### 📊 Comparativo de Modalidades por Período")

        # Gráfico comparativo
        modalidades_geral = dados_geral.get(
            'modalidades', {}) if dados_geral else {}
        modalidades_2024 = dados_2024.get(
            'modalidades', {}) if dados_2024 else {}
        modalidades_2025 = dados_2025.get(
            'modalidades', {}) if dados_2025 else {}

        fig_comparativo = create_modalidades_comparativo_chart(
            modalidades_2024, modalidades_2025, modalidades_geral
        )
        st.plotly_chart(fig_comparativo, use_container_width=True)

        # Tabela comparativa
        st.markdown("#### 📋 Tabela Comparativa")

        import pandas as pd

        # Combinar todas as modalidades
        todas_modalidades = set()
        if modalidades_geral:
            todas_modalidades.update(modalidades_geral.keys())
        if modalidades_2024:
            todas_modalidades.update(modalidades_2024.keys())
        if modalidades_2025:
            todas_modalidades.update(modalidades_2025.keys())

        # Calcular totais para porcentagens
        total_geral = sum(modalidades_geral.values()
                          ) if modalidades_geral else 0
        total_2024 = sum(modalidades_2024.values()) if modalidades_2024 else 0
        total_2025 = sum(modalidades_2025.values()) if modalidades_2025 else 0

        dados_comparativo = []
        for modalidade in sorted(todas_modalidades):
            linha = {'Modalidade': modalidade}

            if modalidades_geral:
                perc_geral = (modalidades_geral.get(modalidade, 0) /
                              total_geral * 100) if total_geral > 0 else 0
                linha['Geral (%)'] = f"{perc_geral:.1f}%"

            if modalidades_2024:
                perc_2024 = (modalidades_2024.get(modalidade, 0) /
                             total_2024 * 100) if total_2024 > 0 else 0
                linha['2024 (%)'] = f"{perc_2024:.1f}%"

            if modalidades_2025:
                perc_2025 = (modalidades_2025.get(modalidade, 0) /
                             total_2025 * 100) if total_2025 > 0 else 0
                linha['2025 (%)'] = f"{perc_2025:.1f}%"

            dados_comparativo.append(linha)

        if dados_comparativo:
            df_comparativo = pd.DataFrame(dados_comparativo)
            st.dataframe(df_comparativo, use_container_width=True,
                         hide_index=True)

        # Insights comparativos
        st.markdown("#### 💡 Insights Comparativos")

        col_comp1, col_comp2, col_comp3 = st.columns(3)

        if modalidades_geral:
            with col_comp1:
                top_geral = max(modalidades_geral.items(), key=lambda x: x[1])
                perc_geral = (top_geral[1] / total_geral *
                              100) if total_geral > 0 else 0
                st.success(f"🏆 **Geral:** {top_geral[0]} ({perc_geral:.1f}%)")

        if modalidades_2024:
            with col_comp2:
                top_2024 = max(modalidades_2024.items(), key=lambda x: x[1])
                perc_2024 = (top_2024[1] / total_2024 *
                             100) if total_2024 > 0 else 0
                st.info(f"📅 **2024:** {top_2024[0]} ({perc_2024:.1f}%)")

        if modalidades_2025:
            with col_comp3:
                top_2025 = max(modalidades_2025.items(), key=lambda x: x[1])
                perc_2025 = (top_2025[1] / total_2025 *
                             100) if total_2025 > 0 else 0
                st.warning(f"🆕 **2025:** {top_2025[0]} ({perc_2025:.1f}%)")

    else:
        st.error("❌ Não foi possível carregar dados para comparativo.")


def render_tabelas_detalhadas(dados_publicos, periodo_texto=""):
    """
    Renderiza tabelas detalhadas dos dados
    """
    titulo = f"📋 Detalhamento dos Dados{' - ' + periodo_texto if periodo_texto else ''}"
    st.markdown(f"### {titulo}")

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
            ]).sort_values('Percentual', key=lambda x: x.str.rstrip(
                '%').astype(float), ascending=False)

            st.dataframe(df_modalidades, use_container_width=True,
                         hide_index=True)
            st.info(
                f"📊 **Total de modalidades:** {len(dados_publicos['modalidades'])}")

    with tab2:
        if dados_publicos['cursos']:
            import pandas as pd

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


def render_insights(dados_publicos, periodo_texto=""):
    """
    Renderiza insights dos dados
    """
    st.markdown("---")
    titulo = f"Insights dos Dados{' - ' + periodo_texto if periodo_texto else ''}"
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
