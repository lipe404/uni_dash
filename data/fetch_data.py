import pandas as pd
import requests
import streamlit as st
from config import GOOGLE_SHEETS_CONFIG
from typing import Optional, Dict, Any
import io


@st.cache_data(ttl=300)  # Cache por 5 minutos
def fetch_google_sheet_data(api_key: str, sheet_id: str, range_name: str) -> Optional[pd.DataFrame]:
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

                # Criar DataFrame
                df = pd.DataFrame(rows, columns=headers)
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


def get_parceiro_vendas_data(parceiro_nome: str) -> Optional[Dict[str, Any]]:
    """
    Retorna dados de vendas específicos de um parceiro
    """
    try:
        df_parceiros = fetch_parceiros_data()

        if df_parceiros is not None:
            parceiro_data = df_parceiros[
                df_parceiros['Parceiro - VENDAS PINCEL + GESTOR'] == parceiro_nome
            ]

            if not parceiro_data.empty:
                data = parceiro_data.iloc[0]

                # Extrair dados mensais
                meses = ['jan./2025', 'fev./2025', 'mar./2025', 'abr./2025',
                         'mai./2025', 'jun./2025', 'jul./2025', 'ago./2025',
                         'set./2025', 'out./2025', 'nov./2025', 'dez./2025']

                vendas_mensais = {}
                for mes in meses:
                    try:
                        valor = pd.to_numeric(
                            data.get(mes, 0), errors='coerce')
                        vendas_mensais[mes] = valor if pd.notna(valor) else 0
                    except:
                        vendas_mensais[mes] = 0

                return {
                    'parceiro': data['Parceiro - VENDAS PINCEL + GESTOR'],
                    'tipo': data['TIPO'],
                    'responsavel': data['RESPONSÁVEL'],
                    'total_2025': pd.to_numeric(data.get('TOTAL 2025', 0), errors='coerce') or 0,
                    'vendas_2024_2025': pd.to_numeric(data.get('VENDAS 2024 + 2025', 0), errors='coerce') or 0,
                    'vendas_mensais': vendas_mensais
                }

        return None

    except Exception as e:
        st.error(f"Erro ao buscar dados do parceiro: {str(e)}")
        return None


def get_dados_publicos_processados() -> Optional[Dict[str, Any]]:
    """
    Processa dados públicos para gráficos
    """
    try:
        df_vendas = fetch_vendas_publicas()

        if df_vendas is not None and not df_vendas.empty:
            # Processar modalidades (Nível)
            modalidades = df_vendas['Nível'].value_counts()

            # Processar cursos
            cursos = df_vendas['Curso'].value_counts().head(
                10)  # Top 10 cursos

            return {
                'modalidades': modalidades.to_dict(),
                'cursos': cursos.to_dict(),
                'total_vendas': len(df_vendas)
            }

        return None

    except Exception as e:
        st.error(f"Erro ao processar dados públicos: {str(e)}")
        return None
