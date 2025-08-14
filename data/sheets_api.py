# Conexão com Google Sheets
import pandas as pd
import requests
import streamlit as st
from config import GOOGLE_SHEETS_CONFIG
from typing import Optional


@st.cache_data(ttl=300)  # Cache por 5 minutos
def fetch_google_sheet_data(
        api_key: str,
        sheet_id: str,
        range_name: str) -> Optional[pd.DataFrame]:
    """
    Busca dados de uma planilha do Google Sheets
    """
    try:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_name}?key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            values = data.get('values', [])

            if values:
                # Primeira linha como cabeçalho
                headers = values[0]
                rows = values[1:]

                # Verificar se todas as linhas têm o mesmo número de colunas
                max_cols = len(headers)

                # Normalizar todas as linhas para ter o mesmo número de colunas
                normalized_rows = []
                for i, row in enumerate(rows):
                    if len(row) < max_cols:
                        row.extend([''] * (max_cols - len(row)))
                    # Se a linha tem mais colunas que o cabeçalho, truncar
                    elif len(row) > max_cols:
                        row = row[:max_cols]
                    normalized_rows.append(row)

                # Criar DataFrame com linhas normalizadas
                df = pd.DataFrame(normalized_rows, columns=headers)

                # Remover linhas completamente vazias
                df = df.dropna(how='all')

                return df
            else:
                st.warning(f"Nenhum dado encontrado na aba: {range_name}")
                return None
        else:
            st.error(f"Erro ao acessar planilha: {response.status_code}")
            return None

    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return None


def fetch_parceiros_data() -> Optional[pd.DataFrame]:
    """
    Busca dados da aba 'Relação de Parceiros'
    """
    config = GOOGLE_SHEETS_CONFIG['planilha_vendas']
    return fetch_google_sheet_data(
        config['API_KEY'],
        config['SHEET_ID'],
        config['abas']['dados_parceiros']
    )


def fetch_vendas_publicas() -> Optional[pd.DataFrame]:
    """
    Busca dados da aba 'Base de Vendas' (dados públicos)
    """
    config = GOOGLE_SHEETS_CONFIG['planilha_vendas']
    return fetch_google_sheet_data(
        config['API_KEY'],
        config['SHEET_ID'],
        config['abas']['base_vendas']
    )
