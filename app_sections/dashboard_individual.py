import streamlit as st
import plotly.express as px
from data.fetch_data import (
    get_parceiro_vendas_data,
    get_evolucao_matriculas_parceiro,
    get_modalidades_parceiro_filtradas,
    get_cursos_parceiro_filtrados,
    get_lista_modalidades_parceiro,
    get_estatisticas_parceiro,
    get_estatisticas_parceiro_filtradas,
    get_modalidades_parceiro_unica,
)
from utils.graphs import (
    create_vendas_mensais_chart,
    create_vendas_acumuladas_chart,
    create_kpi_cards,
    create_evolucao_matriculas_chart,
    create_modalidades_parceiro_bar_chart,
    create_modalidades_parceiro_pie_chart,
    create_cursos_parceiro_chart,
    create_kpi_analise_cards,
    create_modalidades_evolucao_chart,
    create_cursos_modalidade_chart
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
                index=2
            )

        with col_filtro2:
            meses = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }

            mes_atual = datetime.now().month
            meses_opcoes = list(meses.keys())

            try:
                indice_mes_atual = meses_opcoes.index(mes_atual)
            except ValueError:
                indice_mes_atual = 0

            mes_selecionado = st.selectbox(
                "📅 Selecione o Mês:",
                options=meses_opcoes,
                format_func=lambda x: meses[x],
                index=indice_mes_atual
            )

        with col_filtro3:
            if st.button("🔄 Atualizar Dados"):
                st.cache_data.clear()
                st.rerun()

        # Buscar dados de evolução de matrículas
        with st.spinner("Carregando evolução de matrículas..."):
            evolucao_result = get_evolucao_matriculas_parceiro(
                parceiro_nome,
                ano_selecionado,
                mes_selecionado
            )

        if evolucao_result and evolucao_result['evolucao_data']:
            fig_evolucao = create_evolucao_matriculas_chart(
                evolucao_result['evolucao_data'])
            st.plotly_chart(fig_evolucao, use_container_width=True)

            st.metric(
                label="📚 Total de Matrículas no Período",
                value=int(evolucao_result['total_matriculas'])
            )
        else:
            st.info(
                f"Nenhuma matrícula encontrada para {meses[mes_selecionado]} de {ano_selecionado if ano_selecionado else 'todos os anos'}.")

        st.markdown("---")

        st.markdown("### 🎯 Análise Avançada de Modalidades e Cursos")

        # Filtros para análise
        col_filtro_analise1, col_filtro_analise2, col_filtro_analise3, col_filtro_analise4 = st.columns(
            4)

        with col_filtro_analise1:
            ano_analise = st.selectbox(
                "📅 Ano para Análise:",
                options=[2025, 2024, None],
                format_func=lambda x: "Todos os anos" if x is None else str(x),
                index=0,
                key="ano_analise"
            )

        with col_filtro_analise2:
            mes_analise = st.selectbox(
                "📅 Mês para Análise:",
                options=[None] + list(meses.keys()),
                format_func=lambda x: "Todos os meses" if x is None else meses[x],
                index=0,
                key="mes_analise"
            )

        with col_filtro_analise3:
            # Buscar modalidades disponíveis
            modalidades_disponiveis = get_lista_modalidades_parceiro(
                parceiro_nome)
            modalidade_selecionada = st.selectbox(
                "🎯 Modalidade:",
                options=["Todas"] + modalidades_disponiveis,
                index=0,
                key="modalidade_analise"
            )

        with col_filtro_analise4:
            tipo_analise = st.selectbox(
                "📊 Tipo de Análise:",
                options=["Visão Geral", "Comparativo 2025 vs Mês",
                         "Cursos por Modalidade"],
                index=0,
                key="tipo_analise"
            )

        # Definir período para exibição
        if ano_analise and mes_analise:
            periodo_texto = f"{meses[mes_analise]} de {ano_analise}"
        elif ano_analise:
            periodo_texto = f"Ano {ano_analise}"
        elif mes_analise:
            periodo_texto = f"{meses[mes_analise]} (todos os anos)"
        else:
            periodo_texto = "Todo o período"

        # Adicionar modalidade ao texto do período se selecionada
        if modalidade_selecionada and modalidade_selecionada != "Todas":
            periodo_texto += f" - {modalidade_selecionada}"

        # Buscar dados baseados nos filtros
        with st.spinner("Carregando análise avançada..."):
            # Usar estatísticas filtradas que incluem modalidade
            stats_data = get_estatisticas_parceiro_filtradas(
                parceiro_nome,
                ano_analise,
                mes_analise,
                modalidade_selecionada
            )

            if stats_data:
                # KPIs da análise
                st.markdown("#### 📊 Indicadores do Período")
                create_kpi_analise_cards(stats_data, periodo_texto)

                st.markdown("---")

                # Análise baseada no tipo selecionado
                if tipo_analise == "Visão Geral":
                    # Se modalidade específica selecionada, mostrar dados dessa modalidade
                    if modalidade_selecionada and modalidade_selecionada != "Todas":
                        # Dados da modalidade específica
                        modalidades_periodo = get_modalidades_parceiro_unica(
                            parceiro_nome, ano_analise, mes_analise, modalidade_selecionada
                        )
                        cursos_periodo = get_cursos_parceiro_filtrados(
                            parceiro_nome, ano_analise, mes_analise, modalidade_selecionada
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            if modalidades_periodo:
                                fig_modalidades = create_modalidades_parceiro_bar_chart(
                                    modalidades_periodo)
                                fig_modalidades.update_layout(
                                    title=f'🎯 Modalidade: {modalidade_selecionada} - {periodo_texto}')
                                st.plotly_chart(
                                    fig_modalidades, use_container_width=True)

                        with col2:
                            if modalidades_periodo:
                                fig_modalidades_pie = create_modalidades_parceiro_pie_chart(
                                    modalidades_periodo)
                                fig_modalidades_pie.update_layout(
                                    title=f'🥧 {modalidade_selecionada} - {periodo_texto}')
                                st.plotly_chart(
                                    fig_modalidades_pie, use_container_width=True)

                        if cursos_periodo:
                            fig_cursos = create_cursos_modalidade_chart(
                                cursos_periodo, modalidade_selecionada)
                            fig_cursos.update_layout(
                                title=f'📚 Cursos de {modalidade_selecionada} - {periodo_texto}')
                            st.plotly_chart(
                                fig_cursos, use_container_width=True)

                        # Informações específicas da modalidade
                        st.markdown("#### 📋 Resumo da Modalidade")
                        col_resumo1, col_resumo2, col_resumo3 = st.columns(3)

                        with col_resumo1:
                            st.info(
                                f"**📚 Total de Matrículas:** {stats_data['total_matriculas']}")

                        with col_resumo2:
                            st.info(
                                f"**🛒 Total de Vendas:** {stats_data['total_vendas']}")

                        with col_resumo2:
                            st.info(
                                f"**📖 Cursos Diferentes:** {stats_data['variedade_cursos']}")

                    else:
                        # Visão geral de todas as modalidades (comportamento original)
                        modalidades_periodo = get_modalidades_parceiro_filtradas(
                            parceiro_nome, ano_analise, mes_analise)
                        cursos_periodo = get_cursos_parceiro_filtrados(
                            parceiro_nome, ano_analise, mes_analise)

                        col1, col2 = st.columns(2)

                        with col1:
                            if modalidades_periodo:
                                fig_modalidades = create_modalidades_parceiro_bar_chart(
                                    modalidades_periodo)
                                fig_modalidades.update_layout(
                                    title=f'🎯 Modalidades - {periodo_texto}')
                                st.plotly_chart(
                                    fig_modalidades, use_container_width=True)

                        with col2:
                            if modalidades_periodo:
                                fig_modalidades_pie = create_modalidades_parceiro_pie_chart(
                                    modalidades_periodo)
                                fig_modalidades_pie.update_layout(
                                    title=f'🥧 Distribuição - {periodo_texto}')
                                st.plotly_chart(
                                    fig_modalidades_pie, use_container_width=True)

                        if cursos_periodo:
                            fig_cursos = create_cursos_parceiro_chart(
                                cursos_periodo)
                            fig_cursos.update_layout(
                                title=f'🏆 Cursos - {periodo_texto}')
                            st.plotly_chart(
                                fig_cursos, use_container_width=True)

                elif tipo_analise == "Comparativo 2025 vs Mês" and mes_analise:
                    # Comparar total 2025 vs mês específico
                    if modalidade_selecionada and modalidade_selecionada != "Todas":
                        # Comparativo para modalidade específica
                        modalidades_2025 = get_modalidades_parceiro_unica(
                            parceiro_nome, 2025, None, modalidade_selecionada)
                        modalidades_mes = get_modalidades_parceiro_unica(
                            parceiro_nome, 2025, mes_analise, modalidade_selecionada)

                        # Criar gráfico comparativo customizado para modalidade específica
                        if modalidades_2025 and modalidades_mes:
                            fig_comparativo = create_modalidades_evolucao_chart(
                                modalidades_2025,
                                modalidades_mes,
                                meses[mes_analise]
                            )
                            fig_comparativo.update_layout(
                                title=f'📊 {modalidade_selecionada}: Total 2025 vs {meses[mes_analise]}')
                            st.plotly_chart(fig_comparativo,
                                            use_container_width=True)
                        else:
                            st.info(
                                f"Dados insuficientes para comparativo da modalidade {modalidade_selecionada}")
                    else:
                        # Comparativo geral (comportamento original)
                        modalidades_2025 = get_modalidades_parceiro_filtradas(
                            parceiro_nome, 2025, None)
                        modalidades_mes = get_modalidades_parceiro_filtradas(
                            parceiro_nome, 2025, mes_analise)

                        fig_comparativo = create_modalidades_evolucao_chart(
                            modalidades_2025,
                            modalidades_mes,
                            meses[mes_analise]
                        )
                        st.plotly_chart(fig_comparativo,
                                        use_container_width=True)

                elif tipo_analise == "Cursos por Modalidade":
                    # Forçar seleção de modalidade para este tipo de análise
                    if modalidade_selecionada == "Todas":
                        st.warning(
                            "⚠️ Para análise 'Cursos por Modalidade', selecione uma modalidade específica.")
                    else:
                        # Cursos da modalidade específica
                        cursos_modalidade = get_cursos_parceiro_filtrados(
                            parceiro_nome,
                            ano_analise,
                            mes_analise,
                            modalidade_selecionada
                        )

                        if cursos_modalidade:
                            fig_cursos_modalidade = create_cursos_modalidade_chart(
                                cursos_modalidade,
                                modalidade_selecionada
                            )
                            fig_cursos_modalidade.update_layout(
                                title=f'📚 Cursos de {modalidade_selecionada} - {periodo_texto}')
                            st.plotly_chart(fig_cursos_modalidade,
                                            use_container_width=True)

                            # Tabela detalhada dos cursos
                            st.markdown("#### 📋 Detalhamento dos Cursos")
                            import pandas as pd

                            df_cursos_detalhado = pd.DataFrame([
                                {
                                    'Curso': k,
                                    'Matrículas': v,
                                    'Percentual': f"{(v/sum(cursos_modalidade.values())*100):.1f}%"
                                }
                                for k, v in cursos_modalidade.items()
                            ]).sort_values('Matrículas', ascending=False)

                            st.dataframe(
                                df_cursos_detalhado, use_container_width=True, hide_index=True)
                        else:
                            st.info(
                                f"Nenhum curso encontrado para a modalidade '{modalidade_selecionada}' no período selecionado.")

                # Informações adicionais (adaptadas para modalidade específica)
                st.markdown("#### 🏆 Destaques do Período")
                col_destaque1, col_destaque2 = st.columns(2)

                with col_destaque1:
                    modalidade_top = stats_data.get(
                        'modalidade_top', ('Nenhuma', 0))
                    if modalidade_selecionada and modalidade_selecionada != "Todas":
                        st.success(
                            f"**🎯 Modalidade Analisada:** {modalidade_top[0]} ({modalidade_top[1]} matrículas)")
                    else:
                        st.success(
                            f"**🎯 Modalidade Mais Vendida:** {modalidade_top[0]} ({modalidade_top[1]} vendas)")

                with col_destaque2:
                    curso_top = stats_data.get('curso_top', ('Nenhum', 0))
                    # Limitar o nome do curso se for muito longo
                    curso_nome = curso_top[0][:50] + \
                        "..." if len(curso_top[0]) > 50 else curso_top[0]
                    if modalidade_selecionada and modalidade_selecionada != "Todas":
                        st.success(
                            f"**📚 Curso Mais Vendido em {modalidade_selecionada}:** {curso_nome} ({curso_top[1]} vendas)")
                    else:
                        st.success(
                            f"**📚 Curso Mais Vendido:** {curso_nome} ({curso_top[1]} vendas)")

            else:
                st.info(
                    f"Nenhum dado encontrado para o período: {periodo_texto}")

        st.markdown("---")

        # Detalhes mensais (seção original)
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
