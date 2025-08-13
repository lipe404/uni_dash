# Estatísticas
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any
from .partner_data import get_parceiro_vendas_detalhadas


def get_estatisticas_parceiro(
        parceiro_nome: str, ano: int = None, mes: int = None) -> Optional[Dict[str, Any]]:
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

            modalidade_top = max(modalidades_count.items(),
                                 key=lambda x: x[1]) if modalidades_count else ("Nenhuma", 0)

            # Curso mais vendido
            cursos_count = {}
            for _, row in df_filtrado.iterrows():
                curso = row.get('Curso', 'Não informado')
                qtd = row.get('Qtd. Matrículas', 1)
                cursos_count[curso] = cursos_count.get(curso, 0) + qtd

            curso_top = max(cursos_count.items(),
                            key=lambda x: x[1]) if cursos_count else ("Nenhum", 0)

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


def get_estatisticas_parceiro_filtradas(
        parceiro_nome: str,
        ano: int = None, mes: int = None, modalidade: str = None) -> Optional[Dict[str, Any]]:
    """
    Retorna estatísticas gerais do parceiro com filtro de modalidade
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

            # Aplicar filtro de modalidade
            if modalidade and modalidade != "Todas":
                df_filtrado = df_filtrado[df_filtrado['Nível'] == modalidade]

            if df_filtrado.empty:
                return None

            # Calcular estatísticas
            total_matriculas = df_filtrado['Qtd. Matrículas'].sum()
            total_vendas = len(df_filtrado)
            variedade_cursos = df_filtrado['Curso'].nunique()

            # Se filtrado por mod. espec., variedade_modalidades será sempre 1
            variedade_modalidades = 1 if modalidade and modalidade != "Todas" else df_filtrado['Nível'].nunique(
            )

            # Modalidade mais vendida (será a própria modalidade se filtrada)
            if modalidade and modalidade != "Todas":
                modalidade_top = (modalidade, total_matriculas)
            else:
                modalidades_count = {}
                for _, row in df_filtrado.iterrows():
                    nivel = row.get('Nível', 'Não informado')
                    qtd = row.get('Qtd. Matrículas', 1)
                    modalidades_count[nivel] = modalidades_count.get(
                        nivel, 0) + qtd
                modalidade_top = max(modalidades_count.items(),
                                     key=lambda x: x[1]) if modalidades_count else ("Nenhuma", 0)

            # Curso mais vendido
            cursos_count = {}
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
                        cursos_count[curso_individual] = cursos_count.get(
                            curso_individual, 0) + qtd
                else:
                    cursos_count[curso] = cursos_count.get(curso, 0) + qtd

            curso_top = max(cursos_count.items(),
                            key=lambda x: x[1]) if cursos_count else ("Nenhum", 0)

            return {
                'total_matriculas': int(total_matriculas),
                'total_vendas': total_vendas,
                'variedade_cursos': variedade_cursos,
                'variedade_modalidades': variedade_modalidades,
                'modalidade_top': modalidade_top,
                'curso_top': curso_top,
                'modalidade_filtrada': modalidade if modalidade and modalidade != "Todas" else None
            }

        return None

    except Exception as e:
        st.error(
            f"Erro ao calcular estatísticas filtradas do parceiro: {str(e)}")
        return None
