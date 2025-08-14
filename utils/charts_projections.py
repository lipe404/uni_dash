import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def create_sales_projection_chart(vendas_mensais: Dict[str, int],
                                  projecoes: Dict) -> go.Figure:
    """Cria gráfico de vendas com projeções mensais"""

    _month_abbr_to_num = {
        "jan": 1, "fev": 2, "mar": 3, "abr": 4,
        "mai": 5, "jun": 6, "jul": 7, "ago": 8,
        "set": 9, "out": 10, "nov": 11, "dez": 12
    }

    def _parse_month_key_to_date(month_key: str) -> Optional[datetime]:
        try:
            parts = month_key.split('./')
            month_abbr = parts[0].lower()
            year = int(parts[1])
            month_num = _month_abbr_to_num.get(month_abbr)
            if month_num:
                return datetime(year, month_num, 1)
        except (IndexError, ValueError):
            return None
        return None

    # Preparar Dados Históricos
    historical_points = []
    for month_key, sales_value in vendas_mensais.items():
        date_obj = _parse_month_key_to_date(month_key)
        if date_obj and sales_value > 0:
            historical_points.append({'date': date_obj, 'sales': sales_value})

    df_hist = pd.DataFrame(historical_points).sort_values(
        'date').reset_index(drop=True)

    x_historical = df_hist['date'].tolist()
    y_historical = df_hist['sales'].tolist()

    # --- Preparar Dados de Projeção ---
    vendas_projetadas = projecoes.get('projecoes_mensais', [])
    lower_bounds = projecoes.get('lower_bounds_mensais', [])
    upper_bounds = projecoes.get('upper_bounds_mensais', [])

    x_projection = []
    y_projection = []
    y_lower_projection = []
    y_upper_projection = []

    if not df_hist.empty and vendas_projetadas:
        last_historical_date = df_hist['date'].iloc[-1]
        last_historical_sales = df_hist['sales'].iloc[-1]

        # Adicionar o último ponto histórico às séries de projeção
        x_projection.append(last_historical_date)
        y_projection.append(last_historical_sales)
        # Inicia no mesmo ponto
        y_lower_projection.append(last_historical_sales)
        # Inicia no mesmo ponto
        y_upper_projection.append(last_historical_sales)

        current_proj_date = last_historical_date
        for i, proj_sales in enumerate(vendas_projetadas):
            current_proj_date += pd.DateOffset(months=1)
            x_projection.append(current_proj_date)
            y_projection.append(proj_sales)
            y_lower_projection.append(lower_bounds[i])
            y_upper_projection.append(upper_bounds[i])
    else:
        # Se não há histórico, a projeção deve começar de um ponto zero
        pass

    fig = go.Figure()

    # Linha Histórica
    if x_historical and y_historical:
        fig.add_trace(go.Scatter(
            x=x_historical,
            y=y_historical,
            mode='lines+markers',
            name='Vendas Realizadas',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8, color='#1f77b4'),
            hovertemplate='<b>%{x|%b/%Y}</b><br>Vendas: %{y}<extra></extra>'
        ))

    # Cone de Incerteza (área preenchida entre upper e lower)
    if x_projection and y_lower_projection and y_upper_projection and len(
            x_projection) > 1:
        fig.add_trace(go.Scatter(
            x=x_projection + x_projection[::-1],  # X para cima e para baixo
            # Y para cima e para baixo invertido
            y=y_upper_projection + y_lower_projection[::-1],
            fill='toself',
            # Cor da área (laranja translúcido)
            fillcolor='rgba(255,127,14,0.2)',
            line=dict(color='rgba(255,255,255,0)'),  # Linha transparente
            hoverinfo='skip',  # Não mostrar tooltip para essa área
            showlegend=False,
            name='Cone de Incerteza'
        ))

    # Linha de Projeção Média
    if x_projection and y_projection and len(x_projection) > 1:
        fig.add_trace(go.Scatter(
            x=x_projection,
            y=y_projection,
            mode='lines+markers',
            name='Projeção Média',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8, color='#ff7f0e'),
            hovertemplate='<b>%{x|%b/%Y}</b><br>Projeção: %{y}<extra></extra>'
        ))

    fig.update_layout(
        title='📈 Vendas Mensais e Projeções',
        xaxis_title='Meses',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=500,
        hovermode='x unified',
        xaxis=dict(
            tickformat='%b/%Y',
            type='date'
        )
    )

    return fig


def create_cumulative_projection_chart(
        vendas_mensais: Dict[str, int], projecoes: Dict) -> go.Figure:
    """Cria gráfico de vendas acumuladas com projeções"""

    _month_abbr_to_num = {
        "jan": 1, "fev": 2, "mar": 3, "abr": 4,
        "mai": 5, "jun": 6, "jul": 7, "ago": 8,
        "set": 9, "out": 10, "nov": 11, "dez": 12
    }

    def _parse_month_key_to_date(month_key: str) -> Optional[datetime]:
        try:
            parts = month_key.split('./')
            month_abbr = parts[0].lower()
            year = int(parts[1])
            month_num = _month_abbr_to_num.get(month_abbr)
            if month_num:
                return datetime(year, month_num, 1)
        except (IndexError, ValueError):
            return None
        return None

    # Preparar Dados Históricos
    historical_points = []
    for month_key, sales_value in vendas_mensais.items():
        date_obj = _parse_month_key_to_date(month_key)
        if date_obj and sales_value > 0:
            historical_points.append({'date': date_obj, 'sales': sales_value})

    df_hist = pd.DataFrame(historical_points).sort_values(
        'date').reset_index(drop=True)

    df_hist['cumulative_sales'] = df_hist['sales'].cumsum()

    x_historical_cum = df_hist['date'].tolist()
    y_historical_cum = df_hist['cumulative_sales'].tolist()

    # Preparar Dados de Projeção Acumulada
    projecoes_acumuladas = projecoes.get('projecoes_acumuladas', [])
    lower_bounds_acumuladas = projecoes.get('lower_bounds_acumuladas', [])
    upper_bounds_acumuladas = projecoes.get('upper_bounds_acumuladas', [])

    x_projection_cum = []
    y_projection_cum = []
    y_lower_projection_cum = []
    y_upper_projection_cum = []

    if not df_hist.empty and projecoes_acumuladas:
        last_historical_date = df_hist['date'].iloc[-1]
        last_historical_cumulative_sales = df_hist['cumulative_sales'].iloc[-1]

        # Adicionar o último ponto histórico às séries de projeção acumulada
        x_projection_cum.append(last_historical_date)
        y_projection_cum.append(last_historical_cumulative_sales)
        y_lower_projection_cum.append(last_historical_cumulative_sales)
        y_upper_projection_cum.append(last_historical_cumulative_sales)

        current_proj_date = last_historical_date
        for i, proj_cum_sales in enumerate(projecoes_acumuladas):
            current_proj_date += pd.DateOffset(months=1)
            x_projection_cum.append(current_proj_date)
            y_projection_cum.append(proj_cum_sales)
            y_lower_projection_cum.append(lower_bounds_acumuladas[i])
            y_upper_projection_cum.append(upper_bounds_acumuladas[i])
    else:
        pass

    fig = go.Figure()

    # Linha Histórica Acumulada
    if x_historical_cum and y_historical_cum:
        fig.add_trace(go.Scatter(
            x=x_historical_cum,
            y=y_historical_cum,
            mode='lines+markers',
            name='Acumulado Realizado',
            line=dict(color='#2ca02c', width=3),
            marker=dict(size=8, color='#2ca02c'),
            fill='tonexty',
            fillcolor='rgba(44, 160, 44, 0.1)',
            hovertemplate='<b>%{x|%b/%Y}</b><br>Acumulado: %{y}<extra></extra>'
        ))

    # Cone de Incerteza Acumulado
    if x_projection_cum and y_lower_projection_cum and y_upper_projection_cum and len(
            x_projection_cum) > 1:
        fig.add_trace(go.Scatter(
            x=x_projection_cum + x_projection_cum[::-1],
            y=y_upper_projection_cum + y_lower_projection_cum[::-1],
            fill='toself',
            # Cor da área (vermelho translúcido)
            fillcolor='rgba(214,39,40,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo='skip',
            showlegend=False,
            name='Cone de Incerteza Acumulado'
        ))

    # Linha de Projeção Acumulada Média
    if x_projection_cum and y_projection_cum and len(x_projection_cum) > 1:
        fig.add_trace(go.Scatter(
            x=x_projection_cum,
            y=y_projection_cum,
            mode='lines+markers',
            name='Projeção Acumulada Média',
            line=dict(color='#d62728', width=3, dash='dash'),
            marker=dict(size=8, color='#d62728'),
            hovertemplate='<b>%{x|%b/%Y}</b><br>Projeção Acumulada: %{y}<extra></extra>'
        ))

    fig.update_layout(
        title='Vendas Acumuladas e Projeções',
        xaxis_title='Meses',
        yaxis_title='Vendas Acumuladas',
        template='plotly_white',
        height=500,
        hovermode='x unified',
        xaxis=dict(
            tickformat='%b/%Y',
            type='date'
        )
    )

    return fig


def create_targets_comparison_chart(targets: Dict) -> go.Figure:
    """Cria gráfico de comparação com metas"""

    categorias = ['Próximo Mês\n(Projeção)',
                  'Mês Anterior', 'Média do Ano', 'Melhor Mês']

    # Valores principais
    valores_principais = [
        targets['proximo_mes_projecao'],
        targets['mes_anterior_vendas'],
        targets['media_ano_vendas'],
        targets['melhor_mes_vendas']
    ]

    fig = go.Figure()

    # Barras principais
    cores_principais = ['#3498db', '#2ecc71', '#f39c12', '#9b59b6']

    fig.add_trace(go.Bar(
        name='Valores de Referência',
        x=categorias,
        y=valores_principais,
        marker_color=cores_principais,
        text=[f"{val:.0f}" for val in valores_principais],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Valor: %{y}<extra></extra>'
    ))

    # Barras de "falta" (somente onde há diferença)
    categorias_falta = []
    valores_falta_display = []

    # Calcular o que falta
    valores_falta_calc = [
        0,  # Próximo mês (sem falta direta)
        targets['falta_mes_anterior'],
        targets['falta_media_ano'],
        targets['falta_melhor_mes']
    ]

    for i, (cat, falta) in enumerate(zip(categorias, valores_falta_calc)):
        if falta > 0:  # Apenas se há falta
            categorias_falta.append(cat)
            # Parte da barra que representa o atingido
            valores_falta_display.append(valores_principais[i] - falta)
            # Adicionar uma segunda barra para o que falta, em overlay ou group
            fig.add_trace(go.Bar(
                name=f'Falta para {cat}',  # Nome único para legenda
                x=[cat],
                y=[falta],
                marker_color='rgba(231, 76, 60, 0.7)',  # Cor da barra de falta
                textposition='outside',
                hovertemplate=f'<b>{cat}</b><br>Falta: {falta}<extra></extra>',
                showlegend=False,  # Não mostrar na legenda principal
                # Começa onde o "atingido" termina
                base=valores_principais[i] - falta
            ))
        elif falta < 0:  # Se superou, mostrar que superou
            fig.add_trace(go.Bar(
                name=f'Superou {cat}',
                x=[cat],
                y=[abs(falta)],
                marker_color='rgba(44, 160, 44, 0.7)',  # Cor para superação
                textposition='outside',
                hovertemplate=f'<b>{cat}</b><br>Superou: {
                    abs(falta)}<extra></extra>',
                showlegend=False,
                base=valores_principais[i]  # Começa no valor da referência
            ))

    # Linha de referência da projeção
    fig.add_hline(
        y=targets['proximo_mes_projecao'],
        line_dash="dot",
        line_color="rgba(52, 152, 219, 0.8)",
        annotation_text=f"Linha de Projeção: {
            targets['proximo_mes_projecao']}",
        annotation_position="top right"
    )

    fig.update_layout(
        title='🎯 Comparação com Metas e Benchmarks',
        xaxis_title='Categorias',
        yaxis_title='Número de Vendas',
        template='plotly_white',
        height=500,
        barmode='stack',
        showlegend=True
    )

    return fig
