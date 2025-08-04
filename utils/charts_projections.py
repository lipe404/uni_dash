import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
from datetime import datetime


def create_sales_projection_chart(vendas_mensais: Dict[str, int], projecoes: Dict) -> go.Figure:
    """Cria gráfico de vendas com projeções"""

    # Preparar dados históricos
    meses_historicos = []
    vendas_historicas = []

    meses_nomes = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    # Dados históricos
    for i in range(1, 13):
        mes_key = f"{list(meses_nomes.values())[i-1].lower()}./2025"
        if mes_key in vendas_mensais:
            meses_historicos.append(meses_nomes[i])
            vendas_historicas.append(vendas_mensais[mes_key])

    # Dados de projeção
    mes_atual = datetime.now().month
    meses_futuros = []
    vendas_projetadas = projecoes.get('projecoes_mensais', [])

    for i in range(len(vendas_projetadas)):
        mes_futuro = ((mes_atual + i) % 12) + 1
        meses_futuros.append(meses_nomes[mes_futuro])

    fig = go.Figure()

    # Linha histórica
    fig.add_trace(go.Scatter(
        x=meses_historicos,
        y=vendas_historicas,
        mode='lines+markers',
        name='Vendas Realizadas',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate='<b>%{x}</b><br>Vendas: %{y}<extra></extra>'
    ))

    # Linha de projeção
    if vendas_projetadas and meses_futuros:
        # Conectar último ponto histórico com primeiro projetado
        x_conexao = [meses_historicos[-1]
                     if meses_historicos else meses_futuros[0]] + meses_futuros
        y_conexao = [vendas_historicas[-1]
                     if vendas_historicas else 0] + vendas_projetadas

        fig.add_trace(go.Scatter(
            x=x_conexao,
            y=y_conexao,
            mode='lines+markers',
            name='Projeção',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8, color='#ff7f0e'),
            hovertemplate='<b>%{x}</b><br>Projeção: %{y}<extra></extra>'
        ))

    fig.update_layout(
        title='📈 Vendas Mensais e Projeções',
        xaxis_title='Meses',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=500,
        hovermode='x unified'
    )

    return fig


def create_cumulative_projection_chart(vendas_mensais: Dict[str, int], projecoes: Dict) -> go.Figure:
    """Cria gráfico de vendas acumuladas com projeções"""

    # Preparar dados históricos acumulados
    meses_historicos = []
    vendas_acumuladas = []
    acumulado = 0

    meses_nomes = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    # Acumulado histórico
    for i in range(1, 13):
        mes_key = f"{list(meses_nomes.values())[i-1].lower()}./2025"
        if mes_key in vendas_mensais:
            acumulado += vendas_mensais[mes_key]
            meses_historicos.append(meses_nomes[i])
            vendas_acumuladas.append(acumulado)

    # Dados de projeção acumulada
    mes_atual = datetime.now().month
    meses_futuros = []
    projecoes_acumuladas = projecoes.get('projecoes_acumuladas', [])

    for i in range(len(projecoes_acumuladas)):
        mes_futuro = ((mes_atual + i) % 12) + 1
        meses_futuros.append(meses_nomes[mes_futuro])

    fig = go.Figure()

    # Linha histórica acumulada
    fig.add_trace(go.Scatter(
        x=meses_historicos,
        y=vendas_acumuladas,
        mode='lines+markers',
        name='Acumulado Realizado',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8, color='#2ca02c'),
        fill='tonexty',
        fillcolor='rgba(44, 160, 44, 0.1)',
        hovertemplate='<b>%{x}</b><br>Acumulado: %{y}<extra></extra>'
    ))

    # Linha de projeção acumulada
    if projecoes_acumuladas and meses_futuros:
        # Conectar último ponto histórico com projeções
        x_conexao = [meses_historicos[-1]
                     if meses_historicos else meses_futuros[0]] + meses_futuros
        y_conexao = [vendas_acumuladas[-1]
                     if vendas_acumuladas else 0] + projecoes_acumuladas

        fig.add_trace(go.Scatter(
            x=x_conexao,
            y=y_conexao,
            mode='lines+markers',
            name='Projeção Acumulada',
            line=dict(color='#d62728', width=3, dash='dash'),
            marker=dict(size=8, color='#d62728'),
            hovertemplate='<b>%{x}</b><br>Projeção Acumulada: %{y}<extra></extra>'
        ))

    fig.update_layout(
        title='📊 Vendas Acumuladas e Projeções',
        xaxis_title='Meses',
        yaxis_title='Vendas Acumuladas',
        template='plotly_white',
        height=500,
        hovermode='x unified'
    )

    return fig


def create_targets_comparison_chart(targets: Dict) -> go.Figure:
    """Cria gráfico de comparação com metas"""

    categorias = ['Próximo Mês\n(Projeção)',
                  'Mês Anterior', 'Média do Ano', 'Melhor Mês']
    valores_atuais = [
        targets['proximo_mes_projecao'],
        targets['mes_anterior_vendas'],
        targets['media_ano_vendas'],
        targets['melhor_mes_vendas']
    ]

    falta_valores = [
        0,  # Não falta nada para a projeção
        targets['falta_mes_anterior'],
        targets['falta_media_ano'],
        targets['falta_melhor_mes']
    ]

    fig = go.Figure()

    # Barras dos valores atuais/metas
    fig.add_trace(go.Bar(
        name='Valores de Referência',
        x=categorias,
        y=valores_atuais,
        marker_color='#3498db',
        text=valores_atuais,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Valor: %{y}<extra></extra>'
    ))

    # Barras do que falta
    fig.add_trace(go.Bar(
        name='Falta para Atingir',
        x=categorias[1:],  # Excluir "Próximo Mês"
        y=falta_valores[1:],
        marker_color='#e74c3c',
        text=falta_valores[1:],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Falta: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title='🎯 Comparação com Metas e Benchmarks',
        xaxis_title='Categorias',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=500,
        barmode='group'
    )

    return fig
