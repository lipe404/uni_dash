# app_sections/relatorios_metas/components.py
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from utils.report_generator import ReportGenerator


def render_report_filters(modalidades_disponiveis: List[str]) -> tuple:
    """
    Renderiza filtros para relatórios
    Returns: (tipo_relatorio, ano_param, mes_param, modalidades_param)
    """
    st.markdown("#### 🔍 Filtros do Relatório")

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

    return tipo_relatorio, ano_param, mes_param, modalidades_param


def render_preview_metrics(df_preview: pd.DataFrame) -> None:
    """
    Renderiza métricas do preview
    """
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


def render_preview_table(df_preview: pd.DataFrame,
                         tipo_relatorio: str) -> None:
    """
    Renderiza tabela de preview
    """
    if tipo_relatorio == "Dados Detalhados":
        st.markdown("##### 📋 Primeiras 10 linhas:")
        preview_cols = ['Parceiro', 'Aluno', 'Nível', 'Curso', 'IES',
                        'Dt Pagto', 'Qtd. Matrículas', 'Valor Taxa Matrícula']
        preview_cols_disponiveis = [
            col for col in preview_cols if col in df_preview.columns]
        df_show = df_preview[preview_cols_disponiveis].head(10).copy()
        df_show['Dt Pagto'] = df_show['Dt Pagto'].dt.strftime('%d/%m/%Y')

        if 'Valor Taxa Matrícula' in df_show.columns:
            df_show['Valor Taxa Matrícula'] = df_show[
                'Valor Taxa Matrícula'].apply(
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


def render_download_buttons(parceiro_nome: str, tipo_relatorio: str, ano_param, mes_param, modalidades_param) -> None:
    """
    Renderiza botões de download
    """
    st.markdown("#### 📥 Gerar e Baixar Relatório")

    col1, col2, col3 = st.columns(3)
    report_generator = ReportGenerator()

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


def render_report_info() -> None:
    """
    Renderiza informações dos relatórios
    """
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


def render_usage_tips() -> None:
    """
    Renderiza dicas de uso
    """
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

        **🔍 Filtros:**
        - Use filtros específicos para análises direcionadas
        - Combine ano + mês para relatórios mensais
        - Selecione modalidades específicas para análise segmentada
        """)


def render_no_data_suggestions() -> None:
    """
    Renderiza sugestões quando não há dados
    """
    st.warning(
        "Nenhum dado encontrado para os filtros selecionados. Tente ajustar os parâmetros.")

    st.markdown("#### 💡 Sugestões:")
    st.info("""
    - Verifique se o período selecionado possui vendas
    - Tente expandir o filtro para "Todos os anos" ou "Todos os meses"
    - Certifique-se de que as modalidades selecionadas estão corretas
    - Entre em contato com o suporte se o problema persistir
    """)
