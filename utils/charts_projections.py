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

    meses_nomes_completo = {  # Usado para mapear de volta as chaves de vendas_mensais
        1: "jan.", 2: "fev.", 3: "mar.", 4: "abr.",
        5: "mai.", 6: "jun.", 7: "jul.", 8: "ago.",
        9: "set.", 10: "out.", 11: "nov.", 12: "dez."
    }

    # Dados históricos
    meses_historicos = []
    vendas_historicas = []

    current_year = datetime.now().year  # Assumindo o ano de 2025 conforme exemplo

    # Vai até o mês atual ou o último mês com dados
    for i in range(1, datetime.now().month + 1):
        mes_key = f"{meses_nomes_completo[i]}{current_year}"  # Ex: "jan./2025"
        if mes_key in vendas_mensais:
            meses_historicos.append(meses_nomes_curto[i])
            vendas_historicas.append(vendas_mensais[mes_key])
        # Parar de coletar dados históricos se for 0 e não houver mais dados significativos
        # ou se o mês atual for 0 vendas. Se o usuário tiver um mês com 0 vendas, ele aparecerá.
        # A lógica aqui é pegar tudo que está disponível até o presente.

    # Dados de projeção
    meses_futuros = []
    vendas_projetadas = projecoes.get('projecoes_mensais', [])

    # Preencher meses futuros a partir do mês seguinte ao último histórico
    # ou a partir do mês atual se não houver histórico.
    # O primeiro mês a ser projetado
    start_month_for_projection = datetime.now().month + 1

    for i in range(len(vendas_projetadas)):
        # Calcula o mês futuro de forma circular (ex: 12 -> 1 para o próximo ano)
        mes_num_futuro = ((start_month_for_projection + i - 1) % 12) + 1
        meses_futuros.append(meses_nomes_curto[mes_num_futuro])

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
        # Conectar o último ponto histórico com o primeiro ponto projetado
        x_conexao = []
        y_conexao = []

        if meses_historicos:  # Se houver histórico, conecte do último ponto
            x_conexao.append(meses_historicos[-1])
            y_conexao.append(vendas_historicas[-1])
        # else: # Se não houver histórico, a projeção começa do "zero" conceitual,
        #         # mas com o primeiro valor projetado
        #     pass # O primeiro ponto da projeção será o primeiro em meses_futuros/vendas_projetadas

        x_conexao.extend(meses_futuros)
        y_conexao.extend(vendas_projetadas)

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

    meses_nomes_curto = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
    meses_nomes_completo = {
        1: "jan.", 2: "fev.", 3: "mar.", 4: "abr.",
        5: "mai.", 6: "jun.", 7: "jul.", 8: "ago.",
        9: "set.", 10: "out.", 11: "nov.", 12: "dez."
    }

    # Preparar dados históricos acumulados
    meses_historicos = []
    vendas_acumuladas = []
    acumulado = 0
    current_year = datetime.now().year

    # Acumulado histórico
    for i in range(1, datetime.now().month + 1):  # Vai até o mês atual
        mes_key = f"{meses_nomes_completo[i]}{current_year}"
        if mes_key in vendas_mensais:
            acumulado += vendas_mensais[mes_key]
            meses_historicos.append(meses_nomes_curto[i])
            vendas_acumuladas.append(acumulado)

    # Dados de projeção acumulada
    meses_futuros = []
    projecoes_acumuladas = projecoes.get('projecoes_acumuladas', [])

    # Preencher meses futuros a partir do mês seguinte ao último histórico
    start_month_for_projection = datetime.now().month + 1

    for i in range(len(projecoes_acumuladas)):
        mes_num_futuro = ((start_month_for_projection + i - 1) % 12) + 1
        meses_futuros.append(meses_nomes_curto[mes_num_futuro])

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
        # Conectar o último ponto histórico com o primeiro ponto projetado
        x_conexao = []
        y_conexao = []

        if meses_historicos:  # Se houver histórico, conecte do último ponto
            x_conexao.append(meses_historicos[-1])
            y_conexao.append(vendas_acumuladas[-1])

        x_conexao.extend(meses_futuros)
        y_conexao.extend(projecoes_acumuladas)

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

    # Ajustado para considerar que 'falta' pode ser negativa (superou)
    categorias = ['Próximo Mês\n(Projeção)',
                  'Mês Anterior', 'Média do Ano', 'Melhor Mês']
    valores_referencia = [  # Estes são os valores para os quais a projeção é comparada
        # Esta é a própria projeção, não um target a ser batido por outra projeção
        targets['proximo_mes_projecao'],
        targets['mes_anterior_vendas'],
        targets['media_ano_vendas'],
        targets['melhor_mes_vendas']
    ]

    # Diferença da projeção para os benchmarks (projeção - benchmark)
    # Se > 0, superou. Se < 0, falta.
    diferencas_da_projecao = [
        0,  # A projeção é o próprio valor
        targets['proximo_mes_projecao'] - targets['mes_anterior_vendas'],
        targets['proximo_mes_projecao'] - targets['media_ano_vendas'],
        targets['proximo_mes_projecao'] - targets['melhor_mes_vendas']
    ]

    fig = go.Figure()

    # Barras para os valores de referência (Próximo Mês Projeção, Mês Anterior, Média do Ano, Melhor Mês)
    # Mês Anterior, Média do Ano e Melhor Mês são os "alvos"
    fig.add_trace(go.Bar(
        name='Projeção / Benchmark',
        x=categorias,
        y=valores_referencia,
        # Azul para projeção, Verde para benchmarks
        marker_color=['#3498db'] + ['#2ecc71'] * 3,
        text=[f"{val:.0f}" for val in valores_referencia],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Valor: %{y}<extra></extra>'
    ))

    # Barras para a diferença em relação à projeção
    # O que falta (se negativo) ou o que superou (se positivo)
    valores_diferenca = []
    textos_diferenca = []
    cores_diferenca = []

    for i, diff in enumerate(diferencas_da_projecao):
        if i == 0:  # Para "Próximo Mês (Projeção)", não há "falta"
            valores_diferenca.append(0)
            textos_diferenca.append('')
            cores_diferenca.append('rgba(0,0,0,0)')  # Transparente
        elif diff < 0:  # Falta para atingir (diff é negativo)
            valores_diferenca.append(abs(diff))
            textos_diferenca.append(f"Falta {-diff:.0f}")
            cores_diferenca.append('#e74c3c')  # Vermelho
        else:  # Superou o benchmark (diff é positivo ou zero)
            valores_diferenca.append(diff)
            textos_diferenca.append(f"Superou {diff:.0f}")
            cores_diferenca.append('#27ae60')  # Verde

    fig.add_trace(go.Bar(
        name='Diferença vs. Projeção',
        x=categorias,
        y=valores_diferenca,
        marker_color=cores_diferenca,
        text=textos_diferenca,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Diferença: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title='🎯 Comparação com Metas e Benchmarks',
        xaxis_title='Categorias',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=500,
        barmode='group'  # Permite que as barras de referência e diferença fiquem lado a lado
    )

    return fig
