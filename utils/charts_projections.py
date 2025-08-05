import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
from datetime import datetime


def create_sales_projection_chart(vendas_mensais: Dict[str, int], projecoes: Dict) -> go.Figure:
    """Cria gráfico de vendas com projeções mensais"""

    meses_nomes_curto = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    meses_nomes_completo = {
        1: "jan", 2: "fev", 3: "mar", 4: "abr",
        5: "mai", 6: "jun", 7: "jul", 8: "ago",
        9: "set", 10: "out", 11: "nov", 12: "dez"
    }

    # Dados históricos - apenas meses com vendas > 0
    meses_historicos = []
    vendas_historicas = []

    for i in range(1, 13):
        mes_key = f"{meses_nomes_completo[i]}./2025"
        if mes_key in vendas_mensais and vendas_mensais[mes_key] > 0:
            meses_historicos.append(meses_nomes_curto[i])
            vendas_historicas.append(vendas_mensais[mes_key])

    # Dados de projeção - começar do próximo mês após o último histórico
    meses_futuros = []
    vendas_projetadas = projecoes.get('projecoes_mensais', [])

    if meses_historicos:
        # Encontrar o último mês histórico
        ultimo_mes_historico = None
        for i in range(1, 13):
            if meses_nomes_curto[i] == meses_historicos[-1]:
                ultimo_mes_historico = i
                break

        # Projetar a partir do próximo mês
        if ultimo_mes_historico:
            for i in range(len(vendas_projetadas)):
                mes_futuro = ((ultimo_mes_historico + i) % 12) + 1
                meses_futuros.append(meses_nomes_curto[mes_futuro])

    fig = go.Figure()

    # Linha histórica
    if meses_historicos and vendas_historicas:
        fig.add_trace(go.Scatter(
            x=meses_historicos,
            y=vendas_historicas,
            mode='lines+markers',
            name='Vendas Realizadas',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8, color='#1f77b4'),
            hovertemplate='<b>%{x}</b><br>Vendas: %{y}<extra></extra>'
        ))

    # Linha de projeção - conectada ao último ponto histórico
    if vendas_projetadas and meses_futuros and meses_historicos:
        # Conectar do último ponto histórico
        x_projecao = [meses_historicos[-1]] + meses_futuros
        y_projecao = [vendas_historicas[-1]] + vendas_projetadas

        fig.add_trace(go.Scatter(
            x=x_projecao,
            y=y_projecao,
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

    meses_nomes_curto = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    meses_nomes_completo = {
        1: "jan", 2: "fev", 3: "mar", 4: "abr",
        5: "mai", 6: "jun", 7: "jul", 8: "ago",
        9: "set", 10: "out", 11: "nov", 12: "dez"
    }

    # Preparar dados históricos acumulados
    meses_historicos = []
    vendas_acumuladas = []
    acumulado = 0

    for i in range(1, 13):
        mes_key = f"{meses_nomes_completo[i]}./2025"
        if mes_key in vendas_mensais and vendas_mensais[mes_key] > 0:
            acumulado += vendas_mensais[mes_key]
            meses_historicos.append(meses_nomes_curto[i])
            vendas_acumuladas.append(acumulado)

    # Dados de projeção acumulada
    meses_futuros = []
    projecoes_acumuladas = projecoes.get('projecoes_acumuladas', [])

    if meses_historicos:
        # Encontrar o último mês histórico
        ultimo_mes_historico = None
        for i in range(1, 13):
            if meses_nomes_curto[i] == meses_historicos[-1]:
                ultimo_mes_historico = i
                break

        # Projetar a partir do próximo mês
        if ultimo_mes_historico:
            for i in range(len(projecoes_acumuladas)):
                mes_futuro = ((ultimo_mes_historico + i) % 12) + 1
                meses_futuros.append(meses_nomes_curto[mes_futuro])

    fig = go.Figure()

    # Linha histórica acumulada
    if meses_historicos and vendas_acumuladas:
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
    if projecoes_acumuladas and meses_futuros and meses_historicos:
        # Conectar do último ponto histórico
        x_acumulado_proj = [meses_historicos[-1]] + meses_futuros
        y_acumulado_proj = [vendas_acumuladas[-1]] + projecoes_acumuladas

        fig.add_trace(go.Scatter(
            x=x_acumulado_proj,
            y=y_acumulado_proj,
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

    # Valores de referência
    valores_referencia = [
        targets['proximo_mes_projecao'],
        targets['mes_anterior_vendas'],
        targets['media_ano_vendas'],
        targets['melhor_mes_vendas']
    ]

    fig = go.Figure()

    # Barras principais - valores de referência
    cores_barras = ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']

    fig.add_trace(go.Bar(
        name='Valores',
        x=categorias,
        y=valores_referencia,
        marker_color=cores_barras,
        text=[f"{val:.0f}" for val in valores_referencia],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Valor: %{y}<extra></extra>'
    ))

    # Adicionar linha de referência da projeção
    fig.add_hline(
        y=targets['proximo_mes_projecao'],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Projeção: {targets['proximo_mes_projecao']}",
        annotation_position="top right"
    )

    # Barras de diferença (o que falta para atingir)
    valores_falta = [
        0,  # Próximo mês é a própria projeção
        targets['falta_mes_anterior'],
        targets['falta_media_ano'],
        targets['falta_melhor_mes']
    ]

    # Adicionar barras de "falta" apenas onde há diferença positiva
    for i, (categoria, falta) in enumerate(zip(categorias[1:], valores_falta[1:]), 1):
        if falta > 0:
            fig.add_trace(go.Bar(
                name=f'Falta para {categoria}',
                x=[categoria],
                y=[falta],
                marker_color='rgba(231, 76, 60, 0.6)',
                text=[f"Falta: {falta:.0f}"],
                textposition='outside',
                hovertemplate=f'<b>{categoria}</b><br>Falta: {falta}<extra></extra>',
                showlegend=False
            ))

    fig.update_layout(
        title='🎯 Comparação com Metas e Benchmarks',
        xaxis_title='Categorias',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=500,
        barmode='overlay'  # Sobrepor as barras de "falta"
    )

    return fig
