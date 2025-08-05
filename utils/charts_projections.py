import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd  # Certifique-se que pandas está importado
from typing import Dict, List, Optional
from datetime import datetime, timedelta  # timedelta é útil aqui


def create_sales_projection_chart(vendas_mensais: Dict[str, int], projecoes: Dict) -> go.Figure:
    """Cria gráfico de vendas com projeções mensais"""

    # Mapeamento para converter abreviações de meses em números e vice-versa
    _month_abbr_to_num = {
        "jan": 1, "fev": 2, "mar": 3, "abr": 4,
        "mai": 5, "jun": 6, "jul": 7, "ago": 8,
        "set": 9, "out": 10, "nov": 11, "dez": 12
    }
    _num_to_month_abbr = {v: k for k, v in _month_abbr_to_num.items()}

    def _parse_month_key_to_date(month_key: str) -> Optional[datetime]:
        """Converte uma chave de mês como 'jan./2025' para um objeto datetime."""
        try:
            parts = month_key.split('./')
            month_abbr = parts[0].lower()
            year = int(parts[1])
            month_num = _month_abbr_to_num.get(month_abbr)
            if month_num:
                # Usamos o dia 1 para representar o mês
                return datetime(year, month_num, 1)
        except (IndexError, ValueError):
            return None
        return None

    # --- Preparar Dados Históricos ---
    historical_points = []
    # Assumimos que as chaves em vendas_mensais são como 'jan./2025'
    # e que elas podem não vir na ordem exata, então vamos usar as chaves e ordenar.
    for month_key, sales_value in vendas_mensais.items():
        date_obj = _parse_month_key_to_date(month_key)
        if date_obj and sales_value > 0:  # Incluir apenas meses com vendas reais > 0
            historical_points.append({'date': date_obj, 'sales': sales_value})

    # Criar DataFrame para facilitar a ordenação e manipulação, especialmente para datas
    df_hist = pd.DataFrame(historical_points).sort_values(
        'date').reset_index(drop=True)

    # Extrair dados históricos para plotagem
    x_historical = df_hist['date'].tolist()
    y_historical = df_hist['sales'].tolist()

    # --- Preparar Dados de Projeção ---
    vendas_projetadas = projecoes.get('projecoes_mensais', [])

    x_projection = []
    y_projection = []

    if not df_hist.empty:
        last_historical_date = df_hist['date'].iloc[-1]
        last_historical_sales = df_hist['sales'].iloc[-1]

        # Adicionar o último ponto histórico à série de projeção para conectar as linhas
        x_projection.append(last_historical_date)
        y_projection.append(last_historical_sales)

        current_proj_date = last_historical_date
        for proj_sales in vendas_projetadas:
            # Avançar para o próximo mês.
            # pd.DateOffset é a forma mais robusta e recomendada para manipular meses,
            # pois lida automaticamente com viradas de ano, meses com 30/31 dias, etc.
            current_proj_date += pd.DateOffset(months=1)
            x_projection.append(current_proj_date)
            y_projection.append(proj_sales)
    else:
        # Lidar com o caso onde não há dados históricos (pode ser necessário definir um ponto de partida)
        # Por simplicidade, para este bug, assumimos que df_hist não está vazio se houver projeções.
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
            # Formato de data no tooltip
            hovertemplate='<b>%{x|%b/%Y}</b><br>Vendas: %{y}<extra></extra>'
        ))

    # Linha de Projeção
    # Precisa de pelo menos 2 pontos para uma linha
    if x_projection and y_projection and len(x_projection) > 1:
        fig.add_trace(go.Scatter(
            x=x_projection,
            y=y_projection,
            mode='lines+markers',
            name='Projeção',
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
            tickformat='%b/%Y',  # Formato do tick do eixo X (ex: Jan/2025)
            type='date'  # CRUCIAL: Diz ao Plotly para tratar os valores do eixo X como datas
        )
    )

    return fig


def create_cumulative_projection_chart(vendas_mensais: Dict[str, int], projecoes: Dict) -> go.Figure:
    """Cria gráfico de vendas acumuladas com projeções"""

    # Mapeamento para converter abreviações de meses em números
    _month_abbr_to_num = {
        "jan": 1, "fev": 2, "mar": 3, "abr": 4,
        "mai": 5, "jun": 6, "jul": 7, "ago": 8,
        "set": 9, "out": 10, "nov": 11, "dez": 12
    }

    def _parse_month_key_to_date(month_key: str) -> Optional[datetime]:
        """Converte uma chave de mês como 'jan./2025' para um objeto datetime."""
        try:
            parts = month_key.split('./')
            month_abbr = parts[0].lower()
            year = int(parts[1])
            month_num = _month_abbr_to_num.get(month_abbr)
            if month_num:
                # Usamos o dia 1 para representar o mês
                return datetime(year, month_num, 1)
        except (IndexError, ValueError):
            return None
        return None

    # --- Preparar Dados Históricos ---
    historical_points = []
    for month_key, sales_value in vendas_mensais.items():
        date_obj = _parse_month_key_to_date(month_key)
        if date_obj and sales_value > 0:
            historical_points.append({'date': date_obj, 'sales': sales_value})

    df_hist = pd.DataFrame(historical_points).sort_values(
        'date').reset_index(drop=True)

    # Calcular vendas acumuladas históricas
    df_hist['cumulative_sales'] = df_hist['sales'].cumsum()

    x_historical_cum = df_hist['date'].tolist()
    y_historical_cum = df_hist['cumulative_sales'].tolist()

    # --- Preparar Dados de Projeção Acumulada ---
    projecoes_acumuladas = projecoes.get('projecoes_acumuladas', [])

    x_projection_cum = []
    y_projection_cum = []

    if not df_hist.empty:
        last_historical_date = df_hist['date'].iloc[-1]
        last_historical_cumulative_sales = df_hist['cumulative_sales'].iloc[-1]

        # Adicionar o último ponto histórico à série de projeção para conectar as linhas
        x_projection_cum.append(last_historical_date)
        y_projection_cum.append(last_historical_cumulative_sales)

        current_proj_date = last_historical_date
        for proj_cum_sales in projecoes_acumuladas:
            current_proj_date += pd.DateOffset(months=1)
            x_projection_cum.append(current_proj_date)
            y_projection_cum.append(proj_cum_sales)
    else:
        pass  # Lidar com o caso sem dados históricos, se necessário

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

    # Linha de Projeção Acumulada
    if x_projection_cum and y_projection_cum and len(x_projection_cum) > 1:
        fig.add_trace(go.Scatter(
            x=x_projection_cum,
            y=y_projection_cum,
            mode='lines+markers',
            name='Projeção Acumulada',
            line=dict(color='#d62728', width=3, dash='dash'),
            marker=dict(size=8, color='#d62728'),
            hovertemplate='<b>%{x|%b/%Y}</b><br>Projeção Acumulada: %{y}<extra></extra>'
        ))

    fig.update_layout(
        title='📊 Vendas Acumuladas e Projeções',
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
