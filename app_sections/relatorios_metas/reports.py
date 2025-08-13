# app_sections/relatorios_metas/reports.py
import streamlit as st
from typing import List
from utils.report_generator import ReportGenerator
from .components import (
    render_report_filters,
    render_preview_metrics,
    render_preview_table,
    render_download_buttons,
    render_report_info,
    render_usage_tips,
    render_no_data_suggestions
)


def render_reports_section(parceiro_nome: str, modalidades_disponiveis: List[str]) -> None:
    """Renderiza seção de geração de relatórios"""

    st.markdown("### 📄 Geração de Relatórios")

    # Filtros para relatórios
    tipo_relatorio, ano_param, mes_param, modalidades_param = render_report_filters(
        modalidades_disponiveis)

    # Preview dos dados
    st.markdown("#### 👀 Preview dos Dados")

    with st.spinner("Carregando preview..."):
        report_generator = ReportGenerator()
        df_preview = report_generator.get_filtered_sales_data(
            parceiro_nome, ano_param, mes_param, modalidades_param
        )

    if not df_preview.empty:
        # Estatísticas do preview
        render_preview_metrics(df_preview)

        # Tabela de preview
        render_preview_table(df_preview, tipo_relatorio)

        st.markdown("---")

        # Botões de geração
        render_download_buttons(
            parceiro_nome, tipo_relatorio, ano_param, mes_param, modalidades_param)

        # Informações adicionais
        render_report_info()
        render_usage_tips()

    else:
        render_no_data_suggestions()
