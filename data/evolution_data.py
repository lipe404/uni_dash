# Dados de evolução
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any
from .partner_data import get_parceiro_vendas_detalhadas


def get_evolucao_matriculas_parceiro(
        parceiro_nome: str, ano: int = None,
        mes: int = None) -> Optional[Dict[str, Any]]:
    """
    Retorna evolução de matrículas do parceiro por período.
    Agora sempre mostra dados diários para o mês selecionado.
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is None or df_vendas.empty:
            return None

        # Garante que 'Dt Pagto' seja datetime e remove valores NaT
        df_vendas = df_vendas.dropna(subset=['Dt Pagto'])
        if df_vendas.empty:  # Se não houver datas válidas após a limpeza
            return None

        # Filtra por ano se especificado
        if ano:
            df_vendas = df_vendas[df_vendas['Dt Pagto'].dt.year == ano]
            if df_vendas.empty:  # Se não houver dados após filtrar por ano
                return None

        # Sempre filtra por mês e mostra dados diários
        if mes:
            df_vendas = df_vendas[df_vendas['Dt Pagto'].dt.month == mes]
            if df_vendas.empty:  # Se não houver dados após filtrar por mês
                return None

        # Agrupa pela data exata (dia)
        evolucao = df_vendas.groupby(df_vendas['Dt Pagto'].dt.date)[
            'Qtd. Matrículas'].sum().reset_index()
        evolucao = evolucao.rename(columns={'Dt Pagto': 'Periodo'})

        # Converte para string no formato YYYY-MM-DD para garantir consistência
        evolucao['Periodo'] = evolucao['Periodo'].astype(str)

        # Garante a ordem cronológica no gráfico
        evolucao = evolucao.sort_values(by='Periodo')

        return {
            'evolucao_data': evolucao.to_dict('records'),
            'total_matriculas': df_vendas['Qtd. Matrículas'].sum()
        }

    except Exception as e:
        st.error(f"Erro ao calcular evolução de matrículas: {str(e)}")
        return None
