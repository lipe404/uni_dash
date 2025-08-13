# Dados públicos
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any
from .sheets_api import fetch_vendas_publicas


def get_dados_publicos_processados() -> Optional[Dict[str, Any]]:
    """
    Processa dados públicos para gráficos com filtros para dados vazios
    """
    try:
        df_vendas = fetch_vendas_publicas()

        if df_vendas is not None and not df_vendas.empty:
            # Filtrar dados vazios e inválidos
            df_filtrado = df_vendas.dropna(subset=['Nível', 'Curso'])

            # Remove linhas onde Nível ou Curso são strings vazias ou espaços
            df_filtrado = df_filtrado[
                (df_filtrado['Nível'].str.strip() != '') &
                (df_filtrado['Curso'].str.strip() != '')
            ]

            # Remove valores que são apenas "-", "N/A", "null", etc.
            valores_invalidos = ['-', 'n/a', 'null', 'none', '']
            df_filtrado = df_filtrado[
                ~df_filtrado['Nível'].str.lower().str.strip().isin(valores_invalidos) &
                ~df_filtrado['Curso'].str.lower(
                ).str.strip().isin(valores_invalidos)
            ]

            if df_filtrado.empty:
                return None

            # Processar quantidade de matrículas para cálculo correto
            if 'Qtd. Matrículas' in df_filtrado.columns:
                df_filtrado['Qtd. Matrículas'] = pd.to_numeric(
                    df_filtrado['Qtd. Matrículas'], errors='coerce').fillna(1)
            else:
                df_filtrado['Qtd. Matrículas'] = 1

            # Processar modalidades considerando quantidade de matrículas
            modalidades_count = {}
            for _, row in df_filtrado.iterrows():
                nivel = row['Nível'].strip()
                qtd = row['Qtd. Matrículas']
                modalidades_count[nivel] = modalidades_count.get(
                    nivel, 0) + qtd

            # Processar cursos considerando quantidade de matrículas e combos
            cursos_count = {}
            for _, row in df_filtrado.iterrows():
                curso = row['Curso'].strip()
                qtd = row['Qtd. Matrículas']

                # Se for combo, contar cada curso separadamente
                if 'combo' in curso.lower() and ',' in curso:
                    cursos_combo = [c.strip() for c in curso.split(',')]
                    for curso_individual in cursos_combo:
                        if ':' in curso_individual:
                            curso_individual = curso_individual.split(':')[
                                1].strip()
                        if curso_individual:  # Verificar se não está vazio
                            cursos_count[curso_individual] = cursos_count.get(
                                curso_individual, 0) + qtd
                else:
                    cursos_count[curso] = cursos_count.get(curso, 0) + qtd

            # Ordenar e pegar top 10
            modalidades_ordenadas = dict(
                sorted(modalidades_count.items(), key=lambda x: x[1], reverse=True))
            cursos_ordenados = dict(
                sorted(cursos_count.items(), key=lambda x: x[1], reverse=True)[:10])

            # Calcular total de matrículas (não número de linhas)
            total_matriculas = df_filtrado['Qtd. Matrículas'].sum()

            return {
                'modalidades': modalidades_ordenadas,
                'cursos': cursos_ordenados,
                'total_matriculas': int(total_matriculas),
                'total_registros': len(df_filtrado)
            }

        return None

    except Exception as e:
        st.error(f"Erro ao processar dados públicos: {str(e)}")
        return None


def get_dados_publicos_filtrados(ano: int = None, mes: int = None) -> Optional[Dict[str, Any]]:
    """
    Processa dados públicos com filtros de ano e mês
    """
    try:
        df_vendas = fetch_vendas_publicas()

        if df_vendas is not None and not df_vendas.empty:
            # Processar data de pagamento
            if 'Dt Pagto' in df_vendas.columns:
                df_vendas['Dt Pagto'] = pd.to_datetime(
                    df_vendas['Dt Pagto'], format='%d/%m/%Y', errors='coerce')
                # Remove linhas com datas inválidas
                df_vendas = df_vendas.dropna(subset=['Dt Pagto'])

            # Aplicar filtros de data
            df_filtrado = df_vendas.copy()

            if ano:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

            if mes:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

            if df_filtrado.empty:
                return None

            # Filtrar dados vazios e inválidos
            df_filtrado = df_filtrado.dropna(subset=['Nível', 'Curso'])
            df_filtrado = df_filtrado[
                (df_filtrado['Nível'].str.strip() != '') &
                (df_filtrado['Curso'].str.strip() != '')
            ]

            # Remove valores inválidos
            valores_invalidos = ['-', 'n/a', 'null', 'none', '']
            df_filtrado = df_filtrado[
                ~df_filtrado['Nível'].str.lower().str.strip().isin(valores_invalidos) &
                ~df_filtrado['Curso'].str.lower(
                ).str.strip().isin(valores_invalidos)
            ]

            if df_filtrado.empty:
                return None

            # Processar quantidade de matrículas
            if 'Qtd. Matrículas' in df_filtrado.columns:
                df_filtrado['Qtd. Matrículas'] = pd.to_numeric(
                    df_filtrado['Qtd. Matrículas'], errors='coerce').fillna(1)
            else:
                df_filtrado['Qtd. Matrículas'] = 1

            # Processar modalidades
            modalidades_count = {}
            for _, row in df_filtrado.iterrows():
                nivel = row['Nível'].strip()
                qtd = row['Qtd. Matrículas']
                modalidades_count[nivel] = modalidades_count.get(
                    nivel, 0) + qtd

            # Processar cursos
            cursos_count = {}
            for _, row in df_filtrado.iterrows():
                curso = row['Curso'].strip()
                qtd = row['Qtd. Matrículas']

                if 'combo' in curso.lower() and ',' in curso:
                    cursos_combo = [c.strip() for c in curso.split(',')]
                    for curso_individual in cursos_combo:
                        if ':' in curso_individual:
                            curso_individual = curso_individual.split(':')[
                                1].strip()
                        if curso_individual:
                            cursos_count[curso_individual] = cursos_count.get(
                                curso_individual, 0) + qtd
                else:
                    cursos_count[curso] = cursos_count.get(curso, 0) + qtd

            # Ordenar
            modalidades_ordenadas = dict(
                sorted(modalidades_count.items(), key=lambda x: x[1], reverse=True))
            cursos_ordenados = dict(
                sorted(cursos_count.items(), key=lambda x: x[1], reverse=True)[:10])

            total_matriculas = df_filtrado['Qtd. Matrículas'].sum()

            return {
                'modalidades': modalidades_ordenadas,
                'cursos': cursos_ordenados,
                'total_matriculas': int(total_matriculas),
                'total_registros': len(df_filtrado)
            }

        return None

    except Exception as e:
        st.error(f"Erro ao processar dados públicos filtrados: {str(e)}")
        return None


def get_evolucao_modalidades_mensal(ano: int = 2025) -> Optional[Dict[str, Any]]:
    """
    Retorna evolução das modalidades mês a mês para um ano específico
    """
    try:
        df_vendas = fetch_vendas_publicas()

        if df_vendas is not None and not df_vendas.empty:
            # Processar data de pagamento
            if 'Dt Pagto' in df_vendas.columns:
                df_vendas['Dt Pagto'] = pd.to_datetime(
                    df_vendas['Dt Pagto'], format='%d/%m/%Y', errors='coerce')
                df_vendas = df_vendas.dropna(subset=['Dt Pagto'])

            # Filtrar pelo ano
            df_ano = df_vendas[df_vendas['Dt Pagto'].dt.year == ano].copy()

            if df_ano.empty:
                return None

            # Filtrar dados válidos
            df_ano = df_ano.dropna(subset=['Nível'])
            df_ano = df_ano[df_ano['Nível'].str.strip() != '']

            valores_invalidos = ['-', 'n/a', 'null', 'none', '']
            df_ano = df_ano[~df_ano['Nível'].str.lower(
            ).str.strip().isin(valores_invalidos)]

            if df_ano.empty:
                return None

            # Processar quantidade de matrículas
            if 'Qtd. Matrículas' in df_ano.columns:
                df_ano['Qtd. Matrículas'] = pd.to_numeric(
                    df_ano['Qtd. Matrículas'], errors='coerce').fillna(1)
            else:
                df_ano['Qtd. Matrículas'] = 1

            # Adicionar coluna de mês
            df_ano['Mes'] = df_ano['Dt Pagto'].dt.month

            # Calcular dados por mês
            evolucao_data = {}
            meses_nomes = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }

            # Para cada mês, calcular as modalidades
            for mes in range(1, 13):
                df_mes = df_ano[df_ano['Mes'] == mes]

                if not df_mes.empty:
                    modalidades_mes = {}
                    total_mes = 0

                    for _, row in df_mes.iterrows():
                        nivel = row['Nível'].strip()
                        qtd = row['Qtd. Matrículas']
                        modalidades_mes[nivel] = modalidades_mes.get(
                            nivel, 0) + qtd
                        total_mes += qtd

                    # Converter para porcentagens
                    modalidades_percentual = {}
                    if total_mes > 0:
                        for modalidade, qtd in modalidades_mes.items():
                            modalidades_percentual[modalidade] = (
                                qtd / total_mes) * 100

                    evolucao_data[meses_nomes[mes]] = {
                        'modalidades': modalidades_percentual,
                        'total': total_mes
                    }

            return evolucao_data

        return None

    except Exception as e:
        st.error(f"Erro ao calcular evolução mensal das modalidades: {str(e)}")
        return None
