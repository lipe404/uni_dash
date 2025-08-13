import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Optional  # Importar Optional
from data.fetch_data import (
    get_parceiro_vendas_data,
    get_lista_modalidades_parceiro
)
from utils.projections import SalesProjector
from utils.report_generator import ReportGenerator
from utils.charts_projections import (
    create_sales_projection_chart,
    create_cumulative_projection_chart,
    create_targets_comparison_chart
)


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
    tab1, tab2, tab3 = st.tabs(
        ["📊 Projeções e Metas", "📄 Geração de Relatórios", "⚠️ Relatório de Inadimplentes"])

    with tab1:
        render_projections_section(vendas_data, parceiro_nome)

    with tab2:
        render_reports_section(parceiro_nome, modalidades_disponiveis)

    with tab3:
        render_inadimplentes_section(parceiro_nome, modalidades_disponiveis)


def render_projections_section(vendas_data: dict, parceiro_nome: str):
    """Renderiza seção de projeções e metas"""

    st.markdown("### 🔮 Projeções de Vendas")

    # Configurações de projeção
    col1, col2, col3 = st.columns(3)

    with col1:
        meses_projecao = st.selectbox(
            "📅 Meses para Projetar:",
            options=[3, 6, 9, 12],
            index=1,
            help="Número de meses futuros para calcular projeções"
        )

    with col2:
        model_type = st.selectbox(
            "🧠 Modelo de Projeção:",
            options=["Média de Variação",
                     "Regressão Linear", "Média Móvel", "ARIMA"],
            index=0,
            help="Escolha o algoritmo para calcular as projeções."
        )

    with col3:
        if st.button("🔄 Recalcular Projeções"):
            st.cache_data.clear()
            st.rerun()

    # Análise de Cenários "E se..."
    st.markdown("#### 🧪 Análise de Cenários E se...")
    col_scenario1, col_scenario2 = st.columns(2)

    with col_scenario1:
        growth_factor_percent = st.number_input(
            "📈 Fator de Crescimento (%):",
            min_value=-100.0, max_value=100.0, value=0.0, step=1.0, format="%.1f",
            help="Aplique um fator de crescimento percentual à projeção (ex: 10 para +10%)"
        )
    with col_scenario2:
        target_value_scenario = st.number_input(
            " Meta de Vendas Final (Para o período total):",
            min_value=0, value=0, step=1,
            help="Se deseja atingir X vendas até o final do período projetado, digite aqui."
        )

    # Calcular projeções
    with st.spinner("Calculando projeções..."):
        projector = SalesProjector()

        # Passar os parâmetros de modelo e fator de crescimento
        projecoes = projector.calculate_projections(
            vendas_data['vendas_mensais'],
            meses_projecao,
            model_type=model_type,
            growth_factor=growth_factor_percent  # Passa o fator de crescimento aqui
        )

        targets = projector.calculate_targets(
            projecoes, vendas_data['vendas_mensais'])

    # KPIs de projeção
    st.markdown("#### 📈 Indicadores de Projeção")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🔮 Próximo Mês (Projeção)",
            value=targets['proximo_mes_projecao'],
            delta=f"vs Mês Anterior: {targets['mes_anterior_vendas']}"
        )

    with col2:
        st.metric(
            label="📊 Confiabilidade",
            value=projecoes['confiabilidade'],
            delta=f"Base: {projecoes['meses_historicos']} meses"
        )

    with col3:
        st.metric(
            label="📈 Acumulado Atual",
            value=projecoes['vendas_acumuladas_atual'],
            delta=f"Média: {projecoes['media_mensal_atual']}"
        )

    with col4:
        projecao_final = projecoes['projecoes_acumuladas'][-1] if projecoes['projecoes_acumuladas'] else 0
        st.metric(
            label="🎯 Projeção Final",
            value=projecao_final,
            delta=f"em {meses_projecao} meses"
        )

    st.markdown("---")

    # Gráficos de projeção
    col1, col2 = st.columns(2)

    with col1:
        # Passar os resultados completos de projecoes para o gráfico, incluindo os bounds
        fig_mensal = create_sales_projection_chart(
            vendas_data['vendas_mensais'], projecoes)
        st.plotly_chart(fig_mensal, use_container_width=True)

    with col2:
        # Passar os resultados completos de projecoes para o gráfico, incluindo os bounds
        fig_acumulado = create_cumulative_projection_chart(
            vendas_data['vendas_mensais'], projecoes)
        st.plotly_chart(fig_acumulado, use_container_width=True)

    # Gráfico de comparação com metas
    fig_targets = create_targets_comparison_chart(targets)
    st.plotly_chart(fig_targets, use_container_width=True)

    st.markdown("#### 🎯 Análise de Metas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Para Atingir Benchmarks:")

        # Usar targets['falta_mes_anterior'] diretamente, pois já calcula a diferença
        if targets['falta_mes_anterior'] > 0:
            st.warning(
                f"**Mês Anterior:** Faltam {targets['falta_mes_anterior']} vendas para igualar")
        else:
            st.success(
                f"**Mês Anterior:** ✅ Projeção supera em {abs(targets['falta_mes_anterior'])} vendas")

        if targets['falta_media_ano'] > 0:
            st.warning(
                f"**Média do Ano:** Faltam {targets['falta_media_ano']} vendas para igualar")
        else:
            st.success(
                f"**Média do Ano:** ✅ Projeção supera em {abs(targets['falta_media_ano'])} vendas")

        if targets['falta_melhor_mes'] > 0:
            st.warning(
                f"**Melhor Mês:** Faltam {targets['falta_melhor_mes']} vendas para igualar")
        else:
            st.success(
                f"**Melhor Mês:** ✅ Projeção supera em {abs(targets['falta_melhor_mes'])} vendas")

        if target_value_scenario > 0:
            current_total_sales_for_projection_period = projecoes['vendas_acumuladas_atual'] + \
                projecoes['projecoes_acumuladas'][-1] if projecoes['projecoes_acumuladas'] else projecoes['vendas_acumuladas_atual']
            falta_target_scenario = max(
                0, target_value_scenario - current_total_sales_for_projection_period)
            if falta_target_scenario > 0:
                st.info(
                    f"**Meta Cenário:** Faltam {falta_target_scenario} vendas para atingir {target_value_scenario} até o final do período projetado.")
            else:
                st.success(
                    f"**Meta Cenário:** ✅ Projeção atinge {target_value_scenario} (supera em {abs(falta_target_scenario)}).")

    with col2:
        st.markdown("#####  Recomendações:")

        if projecoes['confiabilidade'] == 'Baixa':
            st.info(
                "📈 **Aumente o histórico:** Mais dados melhorarão a precisão das projeções")

        if targets['falta_media_ano'] > 0:
            st.info(
                f" **Foco na meta:** Concentre esforços para atingir {targets['falta_media_ano']} vendas extras")

        if projecoes['media_mensal_atual'] > 0:
            crescimento_necessario = (
                targets['falta_melhor_mes'] / projecoes['media_mensal_atual']) * 100
            if crescimento_necessario > 0:
                st.info(
                    f"📊 **Crescimento necessário:** {crescimento_necessario:.1f}% acima da média para bater o melhor mês")

        st.success(
            "🚀 **Mantenha o ritmo:** Suas projeções mostram tendência positiva!")


def render_reports_section(parceiro_nome: str, modalidades_disponiveis: List[str]):
    """Renderiza seção de geração de relatórios"""

    st.markdown("### 📄 Geração de Relatórios")

    # Filtros para relatórios
    st.markdown("####  Filtros do Relatório")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tipo_relatorio = st.selectbox(
            "📊 Tipo de Relatório:",
            options=["Resumo de Vendas", "Dados Detalhados"],
            help="Resumo: números consolidados | Detalhados: dados individuais dos alunos"
        )

    with col2:
        anos_disponiveis = [2024, 2025]
        ano_relatorio = st.selectbox(
            "📅 Ano:",
            options=["Todos"] + anos_disponiveis,
            index=2  # 2025 por padrão
        )

    with col3:
        meses = {
            "Todos": None,
            "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
            "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
            "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
        }
        mes_relatorio = st.selectbox(
            "📅 Mês:",
            options=list(meses.keys()),
            index=0
        )

    with col4:
        modalidades_selecionadas = st.multiselect(
            "🎯 Modalidades:",
            options=["Todas"] + modalidades_disponiveis,
            default=["Todas"],
            help="Selecione modalidades específicas ou 'Todas'"
        )

    # Preparar parâmetros
    ano_param = None if ano_relatorio == "Todos" else ano_relatorio
    mes_param = meses[mes_relatorio]
    modalidades_param = modalidades_selecionadas if modalidades_selecionadas else [
        "Todas"]

    # Preview dos dados
    st.markdown("#### 👀 Preview dos Dados")

    with st.spinner("Carregando preview..."):
        report_generator = ReportGenerator()
        df_preview = report_generator.get_filtered_sales_data(
            parceiro_nome, ano_param, mes_param, modalidades_param
        )

    if not df_preview.empty:
        # Estatísticas do preview
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📊 Total de Registros", len(df_preview))

        with col2:
            st.metric("📚 Total de Matrículas", int(
                df_preview['Qtd. Matrículas'].sum()))

        with col3:
            st.metric("🎯 Modalidades", df_preview['Nível'].nunique())

        with col4:
            st.metric("📖 Cursos", df_preview['Curso'].nunique())

        # Tabela de preview
        if tipo_relatorio == "Dados Detalhados":
            st.markdown("#####  Primeiras 10 linhas:")
            preview_cols = ['Parceiro', 'Aluno', 'Nível', 'Curso', 'IES',
                            'Dt Pagto', 'Qtd. Matrículas', 'Valor Taxa Matrícula']
            # Filtrar apenas colunas que existem
            preview_cols_disponiveis = [
                col for col in preview_cols if col in df_preview.columns]
            df_show = df_preview[preview_cols_disponiveis].head(10).copy()
            df_show['Dt Pagto'] = df_show['Dt Pagto'].dt.strftime('%d/%m/%Y')

            # Formatar valores monetários no preview
            if 'Valor Taxa Matrícula' in df_show.columns:
                df_show['Valor Taxa Matrícula'] = df_show['Valor Taxa Matrícula'].apply(
                    lambda x: str(x) if pd.notna(x) else "N/A"
                )

            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.markdown("##### 📊 Resumo por Modalidade:")
            resumo = df_preview.groupby(
                'Nível')['Qtd. Matrículas'].sum().reset_index()
            resumo = resumo.sort_values('Qtd. Matrículas', ascending=False)
            resumo.columns = ['Modalidade', 'Total de Matrículas']
            st.dataframe(resumo, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Botões de geração
        st.markdown("#### 📥 Gerar e Baixar Relatório")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### 📊 Excel")
            if st.button("📊 Gerar Excel", key="excel_btn", use_container_width=True):
                with st.spinner("Gerando relatório Excel..."):
                    if tipo_relatorio == "Resumo de Vendas":
                        excel_data = report_generator.generate_summary_report_excel(
                            parceiro_nome, ano_param, mes_param, modalidades_param
                        )
                    else:
                        excel_data = report_generator.generate_detailed_report_excel(
                            parceiro_nome, ano_param, mes_param, modalidades_param
                        )

                    if excel_data:
                        filename = f"relatorio_{parceiro_nome}_{tipo_relatorio.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                        st.download_button(
                            label="⬇️ Baixar Excel",
                            data=excel_data,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_excel"
                        )
                        st.success("✅ Relatório Excel gerado com sucesso!")

        with col2:
            st.markdown("##### 📄 CSV")
            if st.button("📄 Gerar CSV", key="csv_btn", use_container_width=True):
                with st.spinner("Gerando relatório CSV..."):
                    csv_data = report_generator.generate_csv_report(
                        parceiro_nome, ano_param, mes_param, modalidades_param,
                        detailed=(tipo_relatorio == "Dados Detalhados")
                    )

                    if csv_data:
                        filename = f"relatorio_{parceiro_nome}_{tipo_relatorio.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                        st.download_button(
                            label="⬇️ Baixar CSV",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv",
                            key="download_csv"
                        )
                        st.success("✅ Relatório CSV gerado com sucesso!")

        with col3:
            st.markdown("##### 📑 PDF")
            if st.button("📑 Gerar PDF", key="pdf_btn", use_container_width=True):
                with st.spinner("Gerando relatório PDF..."):
                    pdf_data = report_generator.generate_pdf_report(
                        parceiro_nome, ano_param, mes_param, modalidades_param,
                        detailed=(tipo_relatorio == "Dados Detalhados")
                    )

                    if pdf_data:
                        filename = f"relatorio_{parceiro_nome}_{tipo_relatorio.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                        st.download_button(
                            label="⬇️ Baixar PDF",
                            data=pdf_data,
                            file_name=filename,
                            mime="application/pdf",
                            key="download_pdf"
                        )
                        st.success("✅ Relatório PDF gerado com sucesso!")

        # Informações adicionais
        st.markdown("---")
        st.markdown("#### ℹ️ Informações dos Relatórios")

        col1, col2 = st.columns(2)

        with col1:
            st.info("""
            **📊 Resumo de Vendas:**
            - Totais por modalidade e curso
            - Estatísticas consolidadas
            - Gráficos e análises
            - Ideal para apresentações
            """)

        with col2:
            st.info("""
            **📋 Dados Detalhados:**
            - Informações individuais dos alunos
            - Parceiro, nome, curso, IES, data de matrícula
            - Valores das taxas de matrícula
            - Dados completos para análise financeira
            - Ideal para auditoria e controle
            """)

        # Dicas de uso
        with st.expander("💡 Dicas de Uso dos Relatórios"):
            st.markdown("""
            **📊 Excel:**
            - Melhor para análises detalhadas
            - Múltiplas abas organizadas
            - Formatação profissional
            - Fácil manipulação de dados

            **📄 CSV:**
            - Ideal para importação em outros sistemas
            - Formato universal
            - Menor tamanho de arquivo
            - Compatível com qualquer planilha

            **📑 PDF:**
            - Perfeito para apresentações
            - Formato não editável
            - Fácil compartilhamento
            - Visualização profissional

            **Filtros:**
            - Use filtros específicos para análises direcionadas
            - Combine ano + mês para relatórios mensais
            - Selecione modalidades específicas para análise segmentada
            """)

    else:
        st.warning(
            "⚠️ Nenhum dado encontrado para os filtros selecionados. Tente ajustar os parâmetros.")

        # Sugestões quando não há dados
        st.markdown("#### 💡 Sugestões:")
        st.info("""
        - Verifique se o período selecionado possui vendas
        - Tente expandir o filtro para "Todos os anos" ou "Todos os meses"
        - Certifique-se de que as modalidades selecionadas estão corretas
        - Entre em contato com o suporte se o problema persistir
        """)


# FUNÇÃO PARA A SEÇÃO DE INADIMPLENTES
def render_inadimplentes_section(parceiro_nome: str, modalidades_disponiveis: List[str]):
    """Renderiza seção de relatórios de inadimplentes"""

    st.markdown("### ⚠️ Relatório de Alunos Inadimplentes")

    # Alerta explicativo
    st.warning("""
    **📋 Sobre este relatório:**

    Este relatório identifica alunos que **pagaram a taxa de matrícula** mas **NÃO pagaram a primeira mensalidade**.

    - ✅ **Incluídos:** Alunos com status "Não pagou a primeira mensalidade"
    - ❌ **Excluídos:** Cursos que "Não é um curso do Pincel" ou com datas de pagamento registradas.
    """)

    # Verificar se há dados de inadimplentes
    from data.fetch_data import get_inadimplentes_parceiro

    with st.spinner("Verificando dados de inadimplência..."):
        df_inadimplentes_base = get_inadimplentes_parceiro(parceiro_nome)

    if df_inadimplentes_base is None:
        st.error("""
        ❌ **Não foi possível carregar dados de inadimplência.**

        Possíveis causas:
        - As colunas de primeira mensalidade não existem na planilha
        - Não há dados para este parceiro
        - Erro na conexão com a planilha
        """)
        return

    if df_inadimplentes_base.empty:
        st.success("""
        🎉 **Excelente! Não há alunos inadimplentes.**

        Todos os alunos que pagaram a taxa de matrícula também pagaram a primeira mensalidade.
        """)
        return

    # Filtros para relatórios de inadimplentes
    st.markdown("#### 🔍 Filtros do Relatório")

    col1, col2, col3 = st.columns(3)

    with col1:
        anos_disponiveis = [2024, 2025]
        ano_inadimplente = st.selectbox(
            "📅 Ano:",
            options=["Todos"] + anos_disponiveis,
            index=2,  # 2025 por padrão
            key="ano_inadimplente"
        )

    with col2:
        meses = {
            "Todos": None,
            "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
            "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
            "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
        }
        mes_inadimplente = st.selectbox(
            "📅 Mês:",
            options=list(meses.keys()),
            index=0,
            key="mes_inadimplente"
        )

    with col3:
        modalidades_inadimplentes = st.multiselect(
            "🎯 Modalidades:",
            options=["Todas"] + modalidades_disponiveis,
            default=["Todas"],
            help="Selecione modalidades específicas ou 'Todas'",
            key="modalidades_inadimplentes"
        )

    # Preparar parâmetros
    ano_param = None if ano_inadimplente == "Todos" else ano_inadimplente
    mes_param = meses[mes_inadimplente]
    modalidades_param = modalidades_inadimplentes if modalidades_inadimplentes else [
        "Todas"]

    # Buscar dados filtrados
    with st.spinner("Carregando dados de inadimplentes..."):
        from data.fetch_data import get_inadimplentes_filtrados
        df_inadimplentes = get_inadimplentes_filtrados(
            parceiro_nome, ano_param, mes_param, modalidades_param)

    if df_inadimplentes is None or df_inadimplentes.empty:
        st.info("ℹ️ Nenhum aluno inadimplente encontrado para os filtros selecionados.")
        return

    # Estatísticas dos inadimplentes
    st.markdown("####  Estatísticas de Inadimplência")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚠️ Total de Inadimplentes",
            len(df_inadimplentes),
            help="Número total de alunos que não pagaram a primeira mensalidade"
        )

    with col2:
        st.metric(
            "📚 Matrículas Inadimplentes",
            int(df_inadimplentes['Qtd. Matrículas'].sum()),
            help="Soma total de matrículas inadimplentes"
        )

    with col3:
        st.metric(
            "🎯 Modalidades Afetadas",
            df_inadimplentes['Nível'].nunique(),
            help="Número de modalidades com inadimplência"
        )

    with col4:
        st.metric(
            "📖 Cursos Afetados",
            df_inadimplentes['Curso'].nunique(),
            help="Número de cursos com inadimplência"
        )

    # Análise por modalidade
    st.markdown("####  Análise por Modalidade")

    modalidades_inadimplentes_count = df_inadimplentes.groupby(
        'Nível')['Qtd. Matrículas'].sum().reset_index()
    modalidades_inadimplentes_count = modalidades_inadimplentes_count.sort_values(
        'Qtd. Matrículas', ascending=False)
    modalidades_inadimplentes_count.columns = ['Modalidade', 'Inadimplentes']

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            modalidades_inadimplentes_count,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Modalidade": st.column_config.TextColumn("Modalidade"),
                "Inadimplentes": st.column_config.NumberColumn("Inadimplentes", format="%d")
            }
        )

    with col2:
        if len(modalidades_inadimplentes_count) > 0:
            import plotly.express as px
            fig = px.pie(
                modalidades_inadimplentes_count,
                values='Inadimplentes',
                names='Modalidade',
                title="Distribuição de Inadimplentes por Modalidade"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 👀 Preview dos Alunos Inadimplentes")

    # Preparar colunas para exibição
    colunas_preview = ['Aluno', 'Nível', 'Curso',
                       'IES', 'Dt Pagto', 'Qtd. Matrículas']
    colunas_disponiveis = [
        col for col in colunas_preview if col in df_inadimplentes.columns]

    df_preview = df_inadimplentes[colunas_disponiveis].head(20).copy()

    if 'Dt Pagto' in df_preview.columns:
        df_preview['Dt Pagto'] = df_preview['Dt Pagto'].dt.strftime('%d/%m/%Y')

    st.dataframe(
        df_preview,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Aluno": st.column_config.TextColumn("Nome do Aluno"),
            "Nível": st.column_config.TextColumn("Modalidade"),
            "Curso": st.column_config.TextColumn("Curso"),
            "IES": st.column_config.TextColumn("IES"),
            "Dt Pagto": st.column_config.TextColumn("Data da Matrícula"),
            "Qtd. Matrículas": st.column_config.NumberColumn("Qtd. Matrículas")
        }
    )

    if len(df_inadimplentes) > 20:
        st.info(
            f"Mostrando apenas os primeiros 20 registros. Total: {len(df_inadimplentes)} inadimplentes.")

    st.markdown("---")

    # Botões de geração de relatórios
    st.markdown("#### 📥 Gerar Relatório de Inadimplentes")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### 📊 Excel")
        if st.button("📊 Gerar Excel Inadimplentes", key="excel_inadimplentes", use_container_width=True):
            with st.spinner("Gerando relatório de inadimplentes Excel..."):
                report_generator = ReportGenerator()
                excel_data = report_generator.generate_inadimplentes_excel(
                    parceiro_nome, ano_param, mes_param, modalidades_param
                )

                if excel_data:
                    filename = f"inadimplentes_{parceiro_nome}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                    st.download_button(
                        label="⬇️ Baixar Excel Inadimplentes",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel_inadimplentes"
                    )
                    st.success(
                        "✅ Relatório de inadimplentes Excel gerado com sucesso!")

    with col2:
        st.markdown("##### 📄 CSV")
        if st.button("📄 Gerar CSV Inadimplentes", key="csv_inadimplentes", use_container_width=True):
            with st.spinner("Gerando relatório de inadimplentes CSV..."):
                report_generator = ReportGenerator()
                csv_data = report_generator.generate_inadimplentes_csv(
                    parceiro_nome, ano_param, mes_param, modalidades_param
                )

                if csv_data:
                    filename = f"inadimplentes_{parceiro_nome}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                    st.download_button(
                        label="⬇️ Baixar CSV Inadimplentes",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        key="download_csv_inadimplentes"
                    )
                    st.success(
                        "✅ Relatório de inadimplentes CSV gerado com sucesso!")

    with col3:
        st.markdown("##### 📑 PDF")
        if st.button("📑 Gerar PDF Inadimplentes", key="pdf_inadimplentes", use_container_width=True):
            with st.spinner("Gerando relatório de inadimplentes PDF..."):
                report_generator = ReportGenerator()
                pdf_data = report_generator.generate_inadimplentes_pdf(
                    parceiro_nome, ano_param, mes_param, modalidades_param
                )

                if pdf_data:
                    filename = f"inadimplentes_{parceiro_nome}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button(
                        label="⬇️ Baixar PDF Inadimplentes",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        key="download_pdf_inadimplentes"
                    )
                    st.success(
                        "✅ Relatório de inadimplentes PDF gerado com sucesso!")

    # Informações adicionais
    st.markdown("---")
    st.markdown("#### ℹ️ Informações do Relatório de Inadimplentes")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **⚠️ O que são inadimplentes:**
        - Alunos que pagaram a taxa de matrícula
        - Mas NÃO pagaram a primeira mensalidade
        - Status: "Não pagou a primeira mensalidade"
        - Excluídos cursos "Não é um curso do Pincel"
        """)

    with col2:
        st.info("""
        **📋 Dados incluídos no relatório:**
        - Nome completo do aluno
        - Modalidade e curso
        - IES (Instituição de Ensino)
        - Data de pagamento da matrícula
        - Status da primeira mensalidade
        - Quantidade de matrículas
        """)

    # Dicas de uso
    with st.expander("💡 Dicas para Gestão de Inadimplência"):
        st.markdown("""
        **📞 Ações Recomendadas:**

        1. **Contato Imediato:**
           - Entre em contato com os alunos inadimplentes
           - Ofereça opções de pagamento facilitado
           - Esclareça dúvidas sobre o curso

        2. **Análise de Padrões:**
           - Identifique modalidades com maior inadimplência
           - Verifique se há problemas específicos por curso
           - Analise se há concentração em determinados períodos

        3. **Prevenção:**
           - Melhore a comunicação sobre prazos de pagamento
           - Envie lembretes antes do vencimento
           - Ofereça orientação financeira aos alunos

        4. **Monitoramento:**
           - Gere relatórios mensais de inadimplência
           - Acompanhe a evolução dos números
           - Defina metas de redução de inadimplência
        """)
