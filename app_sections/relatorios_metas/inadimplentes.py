# app_sections/relatorios_metas/inadimplentes.py
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List
from utils.report_generator import ReportGenerator


def render_inadimplentes_section(parceiro_nome: str,
                                 modalidades_disponiveis: List[str]) -> None:
    """Renderiza seção de relatórios de inadimplentes"""

    st.markdown("### ⚠️ Relatório de Alunos Inadimplentes")

    # Alerta explicativo
    _render_explanatory_alert()

    # Verificar se há dados de inadimplentes
    df_inadimplentes_base = _check_inadimplentes_data(parceiro_nome)

    if df_inadimplentes_base is None:
        _render_error_state()
        return

    if df_inadimplentes_base.empty:
        _render_success_state()
        return

    # Filtros e processamento
    ano_param, mes_param, modalidades_param = _render_inadimplentes_filters()

    # Buscar dados filtrados
    df_inadimplentes = _get_filtered_inadimplentes(
        parceiro_nome, ano_param, mes_param, modalidades_param)

    if df_inadimplentes is None or df_inadimplentes.empty:
        _render_no_data_state()
        return

    # Renderizar análises
    _render_inadimplentes_metrics(df_inadimplentes)
    _render_modality_analysis(df_inadimplentes)
    _render_inadimplentes_preview(df_inadimplentes)

    st.markdown("---")

    # Botões de download
    _render_inadimplentes_downloads(
        parceiro_nome, ano_param, mes_param, modalidades_param)

    # Informações e dicas
    _render_inadimplentes_info()
    _render_inadimplentes_tips()


def _render_explanatory_alert() -> None:
    """Renderiza alerta explicativo"""
    st.warning("""
    **📋 Sobre este relatório:**

    Este relatório identifica alunos que **pagaram a taxa de matrícula** mas **NÃO pagaram a primeira mensalidade**.

    - ✅ **Incluídos:** Alunos com status "Não pagou a primeira mensalidade"
    - ❌ **Excluídos:** Cursos que "Não é um curso do Pincel" ou com datas de pagamento registradas
    - 🎯 **Modalidades:** Apenas Graduação, Segunda Graduação e Tecnólogo
    """)


def _check_inadimplentes_data(parceiro_nome: str):
    """Verifica se há dados de inadimplentes"""
    from data.fetch_data import get_inadimplentes_parceiro

    with st.spinner("Verificando dados de inadimplência..."):
        return get_inadimplentes_parceiro(parceiro_nome)


def _render_error_state() -> None:
    """Renderiza estado de erro"""
    st.error("""
    ❌ **Não foi possível carregar dados de inadimplência.**

    Possíveis causas:
    - As colunas de primeira mensalidade não existem na planilha
    - Não há dados para este parceiro
    - Erro na conexão com a planilha
    """)


def _render_success_state() -> None:
    """Renderiza estado de sucesso (sem inadimplentes)"""
    st.success("""
    🎉 **Excelente! Não há alunos inadimplentes.**

    Todos os alunos que pagaram a taxa de matrícula também pagaram a primeira mensalidade.
    """)


def _render_inadimplentes_filters() -> tuple:
    """Renderiza filtros para inadimplentes"""
    st.markdown("#### 🔍 Filtros do Relatório")

    col1, col2, col3 = st.columns(3)

    with col1:
        anos_disponiveis = [2024, 2025]
        ano_inadimplente = st.selectbox(
            "📅 Ano:",
            options=["Todos"] + anos_disponiveis,
            index=2,
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
        modalidades_inadimplentes_opcoes = [
            "Todas", "Graduação", "Segunda Graduação", "Tecnólogo"]
        modalidades_inadimplentes = st.multiselect(
            "🎯 Modalidades:",
            options=modalidades_inadimplentes_opcoes,
            default=["Graduação", "Segunda Graduação", "Tecnólogo"],
            help="Modalidades disponíveis para análise de inadimplência",
            key="modalidades_inadimplentes"
        )

    # Preparar parâmetros
    ano_param = None if ano_inadimplente == "Todos" else ano_inadimplente
    mes_param = meses[mes_inadimplente]

    if "Todas" in modalidades_inadimplentes:
        modalidades_param = ["Graduação", "Segunda Graduação", "Tecnólogo"]
    else:
        modalidades_param = modalidades_inadimplentes if modalidades_inadimplentes else [
            "Graduação", "Segunda Graduação", "Tecnólogo"]

    return ano_param, mes_param, modalidades_param


def _get_filtered_inadimplentes(parceiro_nome: str,
                                ano_param,
                                mes_param,
                                modalidades_param):
    """Busca dados filtrados de inadimplentes"""
    from data.fetch_data import get_inadimplentes_filtrados

    with st.spinner("Carregando dados de inadimplentes..."):
        return get_inadimplentes_filtrados(
            parceiro_nome, ano_param, mes_param, modalidades_param)


def _render_no_data_state() -> None:
    """Renderiza estado sem dados"""
    st.info("ℹ️ Nenhum aluno inadimplente encontrado para os filtros selecionados.")
    st.info("""
    **💡 Lembre-se:**
    - Apenas as modalidades **Graduação**, **Segunda Graduação** e **Tecnólogo** são analisadas para inadimplência
    - Outras modalidades não são incluídas neste relatório
    """)


def _render_inadimplentes_metrics(df_inadimplentes: pd.DataFrame) -> None:
    """Renderiza métricas de inadimplentes"""
    st.markdown("#### 📊 Estatísticas de Inadimplência")

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


def _render_modality_analysis(df_inadimplentes: pd.DataFrame) -> None:
    """Renderiza análise por modalidade"""
    st.markdown("#### 📊 Análise por Modalidade")

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
                title="Distribuição de Inadimplentes por Modalidade",
                color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)


def _render_inadimplentes_preview(df_inadimplentes: pd.DataFrame) -> None:
    """Renderiza preview dos inadimplentes"""
    st.markdown("#### Preview dos Alunos Inadimplentes")

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


def _render_inadimplentes_downloads(parceiro_nome: str,
                                    ano_param, mes_param,
                                    modalidades_param) -> None:
    """Renderiza botões de download para inadimplentes"""
    st.markdown("#### 📥 Gerar Relatório de Inadimplentes")

    col1, col2, col3 = st.columns(3)
    report_generator = ReportGenerator()

    with col1:
        st.markdown("##### 📊 Excel")
        if st.button("📊 Gerar Excel Inadimplentes",
                     key="excel_inadimplentes",
                     use_container_width=True):
            with st.spinner("Gerando relatório de inadimplentes Excel..."):
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
        if st.button("📑 Gerar PDF Inadimplentes",
                     key="pdf_inadimplentes",
                     use_container_width=True):
            with st.spinner("Gerando relatório de inadimplentes PDF..."):
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


def _render_inadimplentes_info() -> None:
    """Renderiza informações sobre inadimplentes"""
    st.markdown("---")
    st.markdown("#### ℹ️ Informações do Relatório de Inadimplentes")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **⚠️ O que são inadimplentes:**
        - Alunos que pagaram a taxa de matrícula
        - Mas NÃO pagaram a primeira mensalidade
        - Status: "Não pagou a primeira mensalidade"
        """)

    with col2:
        st.info("""
        **🎯 Modalidades analisadas:**
        - **Graduação:** Cursos de bacharelado e licenciatura
        - **Segunda Graduação:** Segundo curso superior
        - **Tecnólogo:** Cursos de graduação em tecnólogo
        - Outras modalidades não são incluídas neste relatório
        """)


def _render_inadimplentes_tips() -> None:
    """Renderiza dicas para gestão de inadimplência"""
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

        **🎯 Foco nas modalidades principais:**
        - Graduação, Segunda Graduação e Tecnólogo representam o core business
        - Concentre esforços de cobrança nessas modalidades
        - Monitore tendências específicas de cada modalidade
        """)
