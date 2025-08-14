# app_sections/dashboard_individual/dashboard_individual.py
import streamlit as st
from data.fetch_data import (
    get_parceiro_vendas_data,
    get_evolucao_matriculas_parceiro,
    get_lista_modalidades_parceiro,
    get_estatisticas_parceiro_filtradas
)
from .filters import (
    render_evolution_filters,
    render_analysis_filters,
    get_period_text
)
from .kpis import (
    render_main_kpis,
    render_analysis_kpis,
    render_evolution_metric,
    render_highlights
)
from .charts import (
    render_main_charts,
    render_evolution_chart,
    render_no_evolution_data
)
from .analysis import (
    render_general_analysis,
    render_comparative_analysis,
    render_courses_by_modality_analysis
)
from .details import (
    render_monthly_details,
    render_partner_info,
    render_error_state
)


def render_dashboard_individual(parceiro_nome: str):
    """
    Renderiza o dashboard individual do parceiro
    """
    st.title(f"📊 Dashboard - {parceiro_nome}")

    # Buscar dados do parceiro
    with st.spinner("Carregando seus dados..."):
        vendas_data = get_parceiro_vendas_data(parceiro_nome)

    if not vendas_data:
        render_error_state()
        return

    # KPIs principais
    render_main_kpis(vendas_data)
    st.markdown("---")

    # Gráficos principais
    render_main_charts(vendas_data)
    st.markdown("---")

    # Seção de evolução de matrículas
    st.markdown("### 📊 Evolução de Matrículas")
    ano_selecionado, mes_selecionado = render_evolution_filters()

    # Buscar dados de evolução
    with st.spinner("Carregando evolução de matrículas..."):
        evolucao_result = get_evolucao_matriculas_parceiro(
            parceiro_nome, ano_selecionado, mes_selecionado)

    if evolucao_result and evolucao_result['evolucao_data']:
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        render_evolution_chart(evolucao_result['evolucao_data'],
                               meses[mes_selecionado], ano_selecionado)
        render_evolution_metric(evolucao_result)
    else:
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        render_no_evolution_data(meses[mes_selecionado], ano_selecionado)

    st.markdown("---")

    # Seção de análise avançada
    st.markdown("### 🎯 Análise Avançada de Modalidades e Cursos")

    modalidades_disponiveis = get_lista_modalidades_parceiro(parceiro_nome)
    ano_analise, mes_analise, modalidade_selecionada, tipo_analise = render_analysis_filters(
        modalidades_disponiveis)

    periodo_texto = get_period_text(
        ano_analise, mes_analise, modalidade_selecionada)

    # Buscar dados da análise
    with st.spinner("Carregando análise avançada..."):
        stats_data = get_estatisticas_parceiro_filtradas(
            parceiro_nome, ano_analise, mes_analise, modalidade_selecionada)

    if stats_data:
        render_analysis_kpis(stats_data, periodo_texto)
        st.markdown("---")

        # Renderizar análise baseada no tipo selecionado
        if tipo_analise == "Visão Geral":
            render_general_analysis(parceiro_nome, ano_analise,
                                    mes_analise, modalidade_selecionada,
                                    periodo_texto, stats_data)
        elif tipo_analise == "Comparativo 2025 vs Mês" and mes_analise:
            render_comparative_analysis(
                parceiro_nome, mes_analise, modalidade_selecionada)
        elif tipo_analise == "Cursos por Modalidade":
            render_courses_by_modality_analysis(parceiro_nome,
                                                ano_analise,
                                                mes_analise,
                                                modalidade_selecionada,
                                                periodo_texto)

        render_highlights(stats_data, modalidade_selecionada)
    else:
        st.info(f"Nenhum dado encontrado para o período: {periodo_texto}")

    st.markdown("---")

    # Detalhes finais
    render_monthly_details(vendas_data)
    render_partner_info(vendas_data)
