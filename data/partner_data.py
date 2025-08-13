# Dados específicos de parceiros
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any, List
from .sheets_api import fetch_parceiros_data, fetch_vendas_publicas


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
    Retorna dados detalhados de vendas de um parceiro específico.
    """
    try:
        df_vendas = fetch_vendas_publicas()

        if df_vendas is not None and not df_vendas.empty:
            # Filtrar vendas do parceiro específico
            vendas_parceiro = df_vendas[df_vendas['Parceiro']
                                        == parceiro_nome].copy()

            if not vendas_parceiro.empty:
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


def get_modalidades_parceiro_filtradas(
        parceiro_nome: str, ano: int = None, mes: int = None) -> Optional[Dict[str, int]]:
    """
    Retorna modalidades mais vendidas do parceiro com filtros de data
    """
    try:
        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            df_filtrado = df_vendas.copy()

            if ano:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

            if mes:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

            if df_filtrado.empty:
                return None

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


def get_cursos_parceiro_filtrados(
        parceiro_nome: str, ano: int = None,
        mes: int = None, modalidade: str = None) -> Optional[Dict[str, int]]:
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


def get_modalidades_parceiro_unica(
        parceiro_nome: str, ano: int = None,
        mes: int = None, modalidade: str = None) -> Optional[Dict[str, int]]:
    """
    Retorna dados da modalidade específica
    """
    try:
        if not modalidade or modalidade == "Todas":
            return get_modalidades_parceiro_filtradas(parceiro_nome, ano, mes)

        df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

        if df_vendas is not None and not df_vendas.empty:
            # Aplicar filtros
            df_filtrado = df_vendas.copy()

            if ano:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

            if mes:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

            # Filtrar pela modalidade específica
            df_filtrado = df_filtrado[df_filtrado['Nível'] == modalidade]

            if df_filtrado.empty:
                return None

            # Contar apenas a modalidade selecionada
            total_matriculas = df_filtrado['Qtd. Matrículas'].sum()

            return {modalidade: int(total_matriculas)}

        return None

    except Exception as e:
        st.error(f"Erro ao buscar dados da modalidade específica: {str(e)}")
        return None
