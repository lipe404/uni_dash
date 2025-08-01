import pandas as pd
import requests
import streamlit as st
from config import GOOGLE_SHEETS_CONFIG
from typing import Optional, Dict, Any, List
import io
from datetime import datetime, timedelta


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


def get_parceiro_vendas_detalhadas(parceiro_nome: str) -> Optional[pd.DataFrame]:
    """
    Retorna dados detalhados de vendas de um parceiro específico da Base de Vendas
    """
    try:
        df_vendas = fetch_vendas_publicas()

        if df_vendas is not None and not df_vendas.empty:
            # Filtrar vendas do parceiro específico
            vendas_parceiro = df_vendas[df_vendas['Parceiro']
                                        == parceiro_nome].copy()

            if not vendas_parceiro.empty:
                # Processar dados de data
                if 'Dt Pagto' in vendas_parceiro.columns:
                    vendas_parceiro['Dt Pagto'] = pd.to_datetime(
                        vendas_parceiro['Dt Pagto'],
                        format='%d/%m/%Y',
                        errors='coerce'
                    )

                # Processar quantidade de matrículas
                if 'Qtd. Matrículas' in vendas_parceiro.columns:
                    vendas_parceiro['Qtd. Matrículas'] = pd.to_numeric(
                        vendas_parceiro['Qtd. Matrículas'],
                        errors='coerce'
                    ).fillna(1)  # Se não tiver valor, assume 1
                else:
                    vendas_parceiro['Qtd. Matrículas'] = 1

                return vendas_parceiro

        return None

    except Exception as e:
        st.error(f"Erro ao buscar dados detalhados do parceiro: {str(e)}")
        return None


def get_evolucao_matriculas_parceiro(parceiro_nome: str, ano: int = None, mes: int = None) -> Optional[Dict[str, Any]]:
    """
    Retorna evolução de matrículas do parceiro por período.
    Agora sempre mostra dados diários para o mês selecionado.
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is None or df_vendas.empty:
            return None

        # Garante que 'Dt Pagto' seja datetime e remove valores NaT (Not a Time)
        df_vendas = df_vendas.dropna(subset=['Dt Pagto'])
        if df_vendas.empty:  # Se não houver datas válidas após a limpeza
            return None

        # Filtra por ano se especificado
        if ano:
            df_vendas = df_vendas[df_vendas['Dt Pagto'].dt.year == ano]
            if df_vendas.empty:  # Se não houver dados após filtrar por ano
                return None

        # Como sempre temos um mês selecionado, sempre filtra por mês e mostra dados diários
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


def get_modalidades_parceiro_filtradas(parceiro_nome: str, ano: int = None, mes: int = None) -> Optional[Dict[str, int]]:
    """
    Retorna modalidades mais vendidas do parceiro com filtros de data
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            # Aplicar filtros de data
            df_filtrado = df_vendas.copy()

            if ano:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

            if mes:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

            if df_filtrado.empty:
                return None

            # Contar modalidades considerando quantidade de matrículas
            modalidades = {}
            for _, row in df_filtrado.iterrows():
                nivel = row.get('Nível', 'Não informado')
                qtd = row.get('Qtd. Matrículas', 1)
                modalidades[nivel] = modalidades.get(nivel, 0) + qtd

            # Ordenar por quantidade e pegar top 10
            modalidades_ordenadas = dict(
                sorted(modalidades.items(), key=lambda x: x[1], reverse=True)[:10])

            return modalidades_ordenadas

        return None

    except Exception as e:
        st.error(f"Erro ao buscar modalidades filtradas do parceiro: {str(e)}")
        return None


def get_cursos_parceiro_filtrados(parceiro_nome: str, ano: int = None, mes: int = None, modalidade: str = None) -> Optional[Dict[str, int]]:
    """
    Retorna cursos mais vendidos do parceiro com filtros de data e modalidade
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            # Aplicar filtros
            df_filtrado = df_vendas.copy()

            if ano:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

            if mes:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

            if modalidade and modalidade != "Todas":
                df_filtrado = df_filtrado[df_filtrado['Nível'] == modalidade]

            if df_filtrado.empty:
                return None

            # Contar cursos considerando quantidade de matrículas
            cursos = {}
            for _, row in df_filtrado.iterrows():
                curso = row.get('Curso', 'Não informado')
                qtd = row.get('Qtd. Matrículas', 1)

                # Se for combo, contar cada curso separadamente
                if 'combo' in curso.lower() and ',' in curso:
                    # Separar cursos do combo
                    cursos_combo = [c.strip() for c in curso.split(',')]
                    for curso_individual in cursos_combo:
                        if ':' in curso_individual:
                            curso_individual = curso_individual.split(':')[
                                1].strip()
                        cursos[curso_individual] = cursos.get(
                            curso_individual, 0) + qtd
                else:
                    cursos[curso] = cursos.get(curso, 0) + qtd

            # Ordenar por quantidade e pegar top 10
            cursos_ordenados = dict(
                sorted(cursos.items(), key=lambda x: x[1], reverse=True)[:10])

            return cursos_ordenados

        return None

    except Exception as e:
        st.error(f"Erro ao buscar cursos filtrados do parceiro: {str(e)}")
        return None


def get_lista_modalidades_parceiro(parceiro_nome: str) -> List[str]:
    """
    Retorna lista de modalidades disponíveis para o parceiro
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            modalidades = df_vendas['Nível'].dropna().unique().tolist()
            return sorted(modalidades)

        return []

    except Exception as e:
        st.error(f"Erro ao buscar lista de modalidades: {str(e)}")
        return []


def get_estatisticas_parceiro(parceiro_nome: str, ano: int = None, mes: int = None) -> Optional[Dict[str, Any]]:
    """
    Retorna estatísticas gerais do parceiro
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            # Aplicar filtros de data
            df_filtrado = df_vendas.copy()

            if ano:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

            if mes:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

            if df_filtrado.empty:
                return None

            # Calcular estatísticas
            total_matriculas = df_filtrado['Qtd. Matrículas'].sum()
            total_vendas = len(df_filtrado)
            variedade_cursos = df_filtrado['Curso'].nunique()
            variedade_modalidades = df_filtrado['Nível'].nunique()

            # Modalidade mais vendida
            modalidades_count = {}
            for _, row in df_filtrado.iterrows():
                nivel = row.get('Nível', 'Não informado')
                qtd = row.get('Qtd. Matrículas', 1)
                modalidades_count[nivel] = modalidades_count.get(
                    nivel, 0) + qtd

            modalidade_top = max(modalidades_count.items(
            ), key=lambda x: x[1]) if modalidades_count else ("Nenhuma", 0)

            # Curso mais vendido
            cursos_count = {}
            for _, row in df_filtrado.iterrows():
                curso = row.get('Curso', 'Não informado')
                qtd = row.get('Qtd. Matrículas', 1)
                cursos_count[curso] = cursos_count.get(curso, 0) + qtd

            curso_top = max(cursos_count.items(
            ), key=lambda x: x[1]) if cursos_count else ("Nenhum", 0)

            return {
                'total_matriculas': int(total_matriculas),
                'total_vendas': total_vendas,
                'variedade_cursos': variedade_cursos,
                'variedade_modalidades': variedade_modalidades,
                'modalidade_top': modalidade_top,
                'curso_top': curso_top
            }

        return None

    except Exception as e:
        st.error(f"Erro ao calcular estatísticas do parceiro: {str(e)}")
        return None


def get_modalidades_parceiro(parceiro_nome: str) -> Optional[Dict[str, int]]:
    """
    Retorna modalidades mais vendidas do parceiro
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            # Contar modalidades considerando quantidade de matrículas
            modalidades = {}
            for _, row in df_vendas.iterrows():
                nivel = row.get('Nível', 'Não informado')
                qtd = row.get('Qtd. Matrículas', 1)
                modalidades[nivel] = modalidades.get(nivel, 0) + qtd

            # Ordenar por quantidade e pegar top 10
            modalidades_ordenadas = dict(
                sorted(modalidades.items(), key=lambda x: x[1], reverse=True)[:10])

            return modalidades_ordenadas

        return None

    except Exception as e:
        st.error(f"Erro ao buscar modalidades do parceiro: {str(e)}")
        return None


def get_cursos_parceiro(parceiro_nome: str) -> Optional[Dict[str, int]]:
    """
    Retorna cursos mais vendidos do parceiro
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            # Contar cursos considerando quantidade de matrículas
            cursos = {}
            for _, row in df_vendas.iterrows():
                curso = row.get('Curso', 'Não informado')
                qtd = row.get('Qtd. Matrículas', 1)

                # Se for combo, contar cada curso separadamente
                if 'combo' in curso.lower() and ',' in curso:
                    # Separar cursos do combo
                    cursos_combo = [c.strip() for c in curso.split(',')]
                    for curso_individual in cursos_combo:
                        if ':' in curso_individual:
                            curso_individual = curso_individual.split(':')[
                                1].strip()
                        cursos[curso_individual] = cursos.get(
                            curso_individual, 0) + qtd
                else:
                    cursos[curso] = cursos.get(curso, 0) + qtd

            # Ordenar por quantidade e pegar top 10
            cursos_ordenados = dict(
                sorted(cursos.items(), key=lambda x: x[1], reverse=True)[:10])

            return cursos_ordenados

        return None

    except Exception as e:
        st.error(f"Erro ao buscar cursos do parceiro: {str(e)}")
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
