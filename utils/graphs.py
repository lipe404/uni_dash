import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Dict, Any, List
from datetime import date


def create_vendas_mensais_chart(vendas_data: Dict[str, int]) -> go.Figure:
    """
    Cria gráfico de vendas mensais
    """
    meses = list(vendas_data.keys())
    valores = list(vendas_data.values())

    # Simplificar nomes dos meses
    meses_simples = [mes.split('./')[0].capitalize() for mes in meses]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=meses_simples,
        y=valores,
        mode='lines+markers',
        name='Vendas',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))

    fig.update_layout(
        title='📈 Vendas Mensais 2025',
        xaxis_title='Meses',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=400,
        showlegend=False
    )

    return fig


def create_vendas_acumuladas_chart(vendas_data: Dict[str, int]) -> go.Figure:
    """
    Cria gráfico de vendas acumuladas
    """
    meses = list(vendas_data.keys())
    valores = list(vendas_data.values())

    # Calcular acumulado
    acumulado = []
    soma = 0
    for valor in valores:
        soma += valor
        acumulado.append(soma)

    meses_simples = [mes.split('./')[0].capitalize() for mes in meses]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=meses_simples,
        y=acumulado,
        name='Vendas Acumuladas',
        marker_color='#2ca02c',
        text=acumulado,
        textposition='outside'
    ))

    fig.update_layout(
        title='📊 Vendas Acumuladas 2025',
        xaxis_title='Meses',
        yaxis_title='Vendas Acumuladas',
        template='plotly_white',
        height=500,
        showlegend=False
    )

    return fig


def create_evolucao_matriculas_chart(evolucao_data: List[Dict]) -> go.Figure:
    """
    Cria gráfico de evolução de matrículas.
    """
    if not evolucao_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title='📊 Evolução de Matrículas',
            template='plotly_white',
            height=400
        )
        return fig

    df_evolucao = pd.DataFrame(evolucao_data)

    x_values = df_evolucao['Periodo']
    y_values = df_evolucao['Qtd. Matrículas']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines+markers',
        name='Matrículas',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10, color='#e74c3c'),
        fill='tonexty',
        fillcolor='rgba(231, 76, 60, 0.1)'
    ))

    # Determina o título baseado no formato do período
    primeiro_periodo = str(df_evolucao['Periodo'].iloc[0])

    if len(primeiro_periodo) == 10 and primeiro_periodo.count('-') == 2:
        title_text = '📊 Evolução de Matrículas por Dia'
        xaxis_title_text = 'Dia'
    else:
        title_text = '📊 Evolução de Matrículas por Mês'
        xaxis_title_text = 'Mês'

    fig.update_layout(
        title=title_text,
        xaxis_title=xaxis_title_text,
        yaxis_title='Número de Matrículas',
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis=dict(tickangle=45)
    )

    return fig


def create_modalidades_parceiro_bar_chart(modalidades_data: Dict[str, int]) -> go.Figure:
    """
    Cria gráfico de barras das modalidades do parceiro
    """
    if not modalidades_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title='🎯 Top 10 Modalidades Mais Vendidas',
            template='plotly_white',
            height=500
        )
        return fig

    modalidades = list(modalidades_data.keys())[:10]
    valores = list(modalidades_data.values())[:10]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=valores,
        y=modalidades,
        orientation='h',
        marker_color='#9b59b6',
        text=valores,
        textposition='outside'
    ))

    fig.update_layout(
        title='🎯 Top 10 Modalidades Mais Vendidas',
        xaxis_title='Número de Vendas',
        yaxis_title='Modalidades',
        template='plotly_white',
        height=500,
        showlegend=False
    )

    return fig


def create_modalidades_parceiro_pie_chart(modalidades_data: Dict[str, int]) -> go.Figure:
    """
    Cria gráfico de pizza das modalidades do parceiro
    """
    if not modalidades_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title='🥧 Distribuição de Modalidades',
            template='plotly_white',
            height=500
        )
        return fig

    modalidades = list(modalidades_data.keys())
    valores = list(modalidades_data.values())

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=modalidades,
        values=valores,
        hole=0.4,
        textinfo='label+percent',
        textposition='outside',
        marker=dict(colors=px.colors.qualitative.Set3)
    ))

    fig.update_layout(
        title='🥧 Distribuição de Modalidades',
        template='plotly_white',
        height=500
    )

    return fig


def create_cursos_parceiro_chart(cursos_data: Dict[str, int]) -> go.Figure:
    """
    Cria gráfico de barras dos cursos do parceiro
    """
    if not cursos_data:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title='🏆 Top 10 Cursos Mais Vendidos',
            template='plotly_white',
            height=600
        )
        return fig

    cursos = list(cursos_data.keys())[:10]
    valores = list(cursos_data.values())[:10]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=valores,
        y=cursos,
        orientation='h',
        marker_color='#f39c12',
        text=valores,
        textposition='outside'
    ))

    fig.update_layout(
        title='🏆 Top 10 Cursos Mais Vendidos',
        xaxis_title='Número de Vendas',
        yaxis_title='Cursos',
        template='plotly_white',
        height=600,
        showlegend=False
    )

    return fig


def create_modalidades_chart(modalidades_data: Dict[str, int]) -> go.Figure:
    """
    Cria gráfico de modalidades mais vendidas
    """
    modalidades = list(modalidades_data.keys())
    valores = list(modalidades_data.values())

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=modalidades,
        values=valores,
        hole=0.4,
        textinfo='label+percent',
        textposition='outside'
    ))

    fig.update_layout(
        title='🎯 Modalidades Mais Vendidas',
        template='plotly_white',
        height=500
    )

    return fig


def create_cursos_chart(cursos_data: Dict[str, int]) -> go.Figure:
    """
    Cria gráfico de cursos mais vendidos
    """
    cursos = list(cursos_data.keys())[:10]  # Top 10
    valores = list(cursos_data.values())[:10]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=valores,
        y=cursos,
        orientation='h',
        marker_color='#ff7f0e',
        text=valores,
        textposition='outside'
    ))

    fig.update_layout(
        title='🏆 Top 10 Cursos Mais Vendidos',
        xaxis_title='Número de Vendas',
        yaxis_title='Cursos',
        template='plotly_white',
        height=600,
        showlegend=False
    )

    return fig


def create_kpi_cards(vendas_data: Dict[str, Any]):
    """
    Cria cards de KPIs
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📊 Total 2025",
            value=vendas_data.get('total_2025', 0),
            delta=None
        )

    with col2:
        st.metric(
            label="📈 Total Geral (2024 + 2025)",
            value=vendas_data.get('vendas_2024_2025', 0),
            delta=None
        )

    with col3:
        vendas_mensais = vendas_data.get('vendas_mensais', {})
        meses_pt = {
            "01": "Janeiro", "1": "Janeiro",
            "02": "Fevereiro", "2": "Fevereiro",
            "03": "Março", "3": "Março",
            "04": "Abril", "4": "Abril",
            "05": "Maio", "5": "Maio",
            "06": "Junho", "6": "Junho",
            "07": "Julho", "7": "Julho",
            "08": "Agosto", "8": "Agosto",
            "09": "Setembro", "9": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro"
        }
        if vendas_mensais:
            mes_atual_valor = max(vendas_mensais.values())
            mes_nome_raw = [
                mes for mes, valor in vendas_mensais.items() if valor == mes_atual_valor][0]
            # Tenta extrair o número do mês
            import re
            match = re.search(r'(\d{1,2})', mes_nome_raw)
            if match:
                mes_num = match.group(1).zfill(2)
                mes_nome_extenso = meses_pt.get(mes_num, mes_nome_raw)
            else:
                mes_nome_extenso = mes_nome_raw
            valor_melhor_mes = f"{mes_nome_extenso} : {int(mes_atual_valor)}"
        else:
            valor_melhor_mes = "- : 0"
        st.metric(
            label="🔥 Melhor Mês",
            value=valor_melhor_mes,
            delta=None
        )

    with col4:
        media_mensal = sum(vendas_mensais.values()) / \
            len(vendas_mensais) if vendas_mensais else 0
        st.metric(
            label="📊 Média Mensal",
            value=f"{media_mensal:.1f}",
            delta=None
        )


def create_kpi_analise_cards(stats_data: Dict[str, Any], periodo_texto: str):
    """
    Cria cards de KPIs para análise de modalidades e cursos
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📚 Total de Matrículas",
            value=stats_data.get('total_matriculas', 0),
            help=f"Total de matrículas no período: {periodo_texto}"
        )

    with col2:
        st.metric(
            label="🛒 Total de Vendas",
            value=stats_data.get('total_vendas', 0),
            help=f"Número de transações no período: {periodo_texto}"
        )

    with col3:
        st.metric(
            label="🎯 Variedade de Modalidades",
            value=stats_data.get('variedade_modalidades', 0),
            help=f"Diferentes modalidades vendidas no período: {periodo_texto}"
        )

    with col4:
        st.metric(
            label="📖 Variedade de Cursos",
            value=stats_data.get('variedade_cursos', 0),
            help=f"Diferentes cursos vendidos no período: {periodo_texto}"
        )


def create_modalidades_evolucao_chart(modalidades_2025: Dict[str, int], modalidades_mensal: Dict[str, int], mes_nome: str) -> go.Figure:
    """
    Cria gráfico comparativo de modalidades (2025 vs mês específico)
    """
    if not modalidades_2025 and not modalidades_mensal:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title='📊 Comparativo de Modalidades',
            template='plotly_white',
            height=500
        )
        return fig

    # Combinar todas as modalidades
    todas_modalidades = set(modalidades_2025.keys() if modalidades_2025 else []) | set(
        modalidades_mensal.keys() if modalidades_mensal else [])

    modalidades_list = list(todas_modalidades)
    valores_2025 = [modalidades_2025.get(
        mod, 0) if modalidades_2025 else 0 for mod in modalidades_list]
    valores_mensal = [modalidades_mensal.get(
        mod, 0) if modalidades_mensal else 0 for mod in modalidades_list]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Total 2025',
        x=modalidades_list,
        y=valores_2025,
        marker_color='#3498db',
        text=valores_2025,
        textposition='outside'
    ))

    fig.add_trace(go.Bar(
        name=f'{mes_nome}',
        x=modalidades_list,
        y=valores_mensal,
        marker_color='#e74c3c',
        text=valores_mensal,
        textposition='outside'
    ))

    fig.update_layout(
        title=f'📊 Modalidades: Total 2025 vs {mes_nome}',
        xaxis_title='Modalidades',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=500,
        barmode='group',
        xaxis=dict(tickangle=45)
    )

    return fig


def create_cursos_modalidade_chart(cursos_data: Dict[str, int], modalidade: str) -> go.Figure:
    """
    Cria gráfico de cursos mais vendidos por modalidade específica
    """
    if not cursos_data:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Nenhum curso encontrado para a modalidade: {modalidade}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title=f'📚 Cursos da Modalidade: {modalidade}',
            template='plotly_white',
            height=500
        )
        return fig

    cursos = list(cursos_data.keys())[:10]
    valores = list(cursos_data.values())[:10]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=valores,
        y=cursos,
        orientation='h',
        marker_color='#27ae60',
        text=valores,
        textposition='outside'
    ))

    fig.update_layout(
        title=f'📚 Top 10 Cursos - {modalidade}',
        xaxis_title='Número de Vendas',
        yaxis_title='Cursos',
        template='plotly_white',
        height=500,
        showlegend=False
    )

    return fig
