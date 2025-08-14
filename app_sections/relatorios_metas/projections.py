# app_sections/relatorios_metas/projections.py
import streamlit as st
from typing import Dict, Any
from utils.projections import SalesProjector
from utils.charts_projections import (
    create_sales_projection_chart,
    create_cumulative_projection_chart,
    create_targets_comparison_chart
)


def render_projections_section(vendas_data: Dict[str, Any],
                               parceiro_nome: str) -> None:
    """Renderiza seção de projeções e metas"""

    st.markdown("### 🔮 Projeções de Vendas")

    # Configurações de projeção
    meses_projecao, model_type, growth_factor_percent, target_value_scenario = _render_projection_controls()

    # Calcular projeções
    projecoes, targets = _calculate_projections(
        vendas_data, meses_projecao, model_type, growth_factor_percent)

    # KPIs de projeção
    _render_projection_kpis(projecoes, targets, meses_projecao)

    st.markdown("---")

    # Gráficos de projeção
    _render_projection_charts(vendas_data, projecoes, targets)

    # Análise de metas
    _render_targets_analysis(projecoes, targets, target_value_scenario)


def _render_projection_controls() -> tuple:
    """
    Renderiza controles de configuração de projeção
    """
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
            "🎯 Meta de Vendas Final (Para o período total):",
            min_value=0, value=0, step=1,
            help="Se deseja atingir X vendas até o final do período projetado, digite aqui."
        )

    return meses_projecao, model_type, growth_factor_percent, target_value_scenario


def _calculate_projections(vendas_data: Dict[str, Any],
                           meses_projecao: int,
                           model_type: str,
                           growth_factor_percent: float) -> tuple:
    """
    Calcula projeções e targets
    """
    with st.spinner("Calculando projeções..."):
        projector = SalesProjector()

        projecoes = projector.calculate_projections(
            vendas_data['vendas_mensais'],
            meses_projecao,
            model_type=model_type,
            growth_factor=growth_factor_percent
        )

        targets = projector.calculate_targets(
            projecoes, vendas_data['vendas_mensais'])

    return projecoes, targets


def _render_projection_kpis(projecoes: Dict[str, Any],
                            targets: Dict[str, Any],
                            meses_projecao: int) -> None:
    """
    Renderiza KPIs de projeção
    """
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


def _render_projection_charts(vendas_data: Dict[str, Any],
                              projecoes: Dict[str, Any],
                              targets: Dict[str, Any]) -> None:
    """
    Renderiza gráficos de projeção
    """
    col1, col2 = st.columns(2)

    with col1:
        fig_mensal = create_sales_projection_chart(
            vendas_data['vendas_mensais'], projecoes)
        st.plotly_chart(fig_mensal, use_container_width=True)

    with col2:
        fig_acumulado = create_cumulative_projection_chart(
            vendas_data['vendas_mensais'], projecoes)
        st.plotly_chart(fig_acumulado, use_container_width=True)

    # Gráfico de comparação com metas
    fig_targets = create_targets_comparison_chart(targets)
    st.plotly_chart(fig_targets, use_container_width=True)


def _render_targets_analysis(projecoes: Dict[str, Any],
                             targets: Dict[str, Any],
                             target_value_scenario: int) -> None:
    """
    Renderiza análise de metas
    """
    st.markdown("#### 🎯 Análise de Metas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Para Atingir Benchmarks:")

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
        st.markdown("##### 💡 Recomendações:")

        if projecoes['confiabilidade'] == 'Baixa':
            st.info(
                "📈 **Aumente o histórico:** Mais dados melhorarão a precisão das projeções")

        if targets['falta_media_ano'] > 0:
            st.info(
                f"🎯 **Foco na meta:** Concentre esforços para atingir {targets['falta_media_ano']} vendas extras")

        if projecoes['media_mensal_atual'] > 0:
            crescimento_necessario = (
                targets['falta_melhor_mes'] / projecoes['media_mensal_atual']) * 100
            if crescimento_necessario > 0:
                st.info(
                    f"📊 **Crescimento necessário:** {crescimento_necessario:.1f}% acima da média para bater o melhor mês")

        st.success(
            "🚀 **Mantenha o ritmo:** Suas projeções mostram tendência positiva!")
