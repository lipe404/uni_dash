import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Dict, Any, List


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
        height=400,
        showlegend=False
    )

    return fig


def create_evolucao_matriculas_chart(evolucao_data: List[Dict]) -> go.Figure:
    """
    Cria gráfico de evolução de matrículas
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

    meses = [item['Mes_Ano_Str'] for item in evolucao_data]
    matriculas = [item['Qtd. Matrículas'] for item in evolucao_data]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=meses,
        y=matriculas,
        mode='lines+markers',
        name='Matrículas',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10, color='#e74c3c'),
        fill='tonexty',
        fillcolor='rgba(231, 76, 60, 0.1)'
    ))

    fig.update_layout(
        title='📊 Evolução de Matrículas por Mês',
        xaxis_title='Período',
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
            label="📈 Total Geral",
            value=vendas_data.get('vendas_2024_2025', 0),
            delta=None
        )

    with col3:
        vendas_mensais = vendas_data.get('vendas_mensais', {})
        mes_atual = max(vendas_mensais.values()) if vendas_mensais else 0
        st.metric(
            label="🔥 Melhor Mês",
            value=int(mes_atual),
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
