# Dados de inadimplentes
# data/inadimplentes_data.py
import pandas as pd
import streamlit as st
from typing import Optional, List
from .sheets_api import fetch_vendas_publicas


def get_inadimplentes_parceiro(parceiro_nome: str) -> Optional[pd.DataFrame]:
    """
    Retorna dados de alunos inadimplentes (que pagaram taxa de matrícula mas não pagaram primeira mensalidade)
    """
    try:
        df_vendas = fetch_vendas_publicas()

        if df_vendas is not None and not df_vendas.empty:
            # Filtrar vendas do parceiro específico
            vendas_parceiro = df_vendas[df_vendas['Parceiro']
                                        == parceiro_nome].copy()

            if not vendas_parceiro.empty:
                # Buscar colunas de primeira mensalidade com diferentes variações de nome
                colunas_primeira_mensalidade_dt = [
                    'Primeira Mensalidade Dt. Pagto',
                    'Primeira Mensalidade\nDt. Pagto',
                    'Primeira Mensalidade Dt Pagto',
                    'Primeira MensalidadeDt. Pagto'
                ]

                colunas_primeira_mensalidade_valor = [
                    'Primeira Mensalidade Valor. Pagto',
                    'Primeira Mensalidade\nValor. Pagto',
                    'Primeira Mensalidade Valor Pagto',
                    'Primeira MensalidadeValor. Pagto'
                ]

                # Encontrar as colunas corretas
                col_dt_encontrada = None
                col_valor_encontrada = None

                for col in colunas_primeira_mensalidade_dt:
                    if col in vendas_parceiro.columns:
                        col_dt_encontrada = col
                        break

                for col in colunas_primeira_mensalidade_valor:
                    if col in vendas_parceiro.columns:
                        col_valor_encontrada = col
                        break

                # Se não encontrou as colunas exatas, tentar busca por substring
                if not col_dt_encontrada:
                    for col in vendas_parceiro.columns:
                        if 'primeira mensalidade' in col.lower() and ('dt' in col.lower() or 'data' in col.lower()):
                            col_dt_encontrada = col
                            break

                if not col_valor_encontrada:
                    for col in vendas_parceiro.columns:
                        if 'primeira mensalidade' in col.lower() and 'valor' in col.lower():
                            col_valor_encontrada = col
                            break

                if col_dt_encontrada and col_valor_encontrada:
                    # Filtrar apenas alunos que não pagaram a primeira mensalidade
                    inadimplentes = vendas_parceiro[
                        (vendas_parceiro[col_dt_encontrada] == 'Não pagou a primeira mensalidade.') |
                        (vendas_parceiro[col_valor_encontrada]
                         == 'Não pagou a primeira mensalidade.')
                    ].copy()

                    if not inadimplentes.empty:
                        # Processar dados de data de pagamento da matrícula
                        if 'Dt Pagto' in inadimplentes.columns:
                            inadimplentes['Dt Pagto'] = pd.to_datetime(
                                inadimplentes['Dt Pagto'],
                                format='%d/%m/%Y',
                                errors='coerce'
                            )

                        # Processar quantidade de matrículas
                        if 'Qtd. Matrículas' in inadimplentes.columns:
                            inadimplentes['Qtd. Matrículas'] = pd.to_numeric(
                                inadimplentes['Qtd. Matrículas'],
                                errors='coerce'
                            ).fillna(1)
                        else:
                            inadimplentes['Qtd. Matrículas'] = 1

                        # Padronizar nomes das colunas para facilitar o uso posterior
                        inadimplentes = inadimplentes.rename(columns={
                            col_dt_encontrada: 'Primeira Mensalidade Dt. Pagto',
                            col_valor_encontrada: 'Primeira Mensalidade Valor. Pagto'
                        })

                        return inadimplentes
                    else:
                        st.info(
                            "Nenhum aluno inadimplente encontrado para este parceiro.")
                        return pd.DataFrame()
                else:
                    # Mostrar quais colunas estão disponíveis que contêm "primeira mensalidade"
                    colunas_relacionadas = [
                        col for col in vendas_parceiro.columns if 'primeira mensalidade' in col.lower()]
                    if colunas_relacionadas:
                        st.warning(
                            f"Colunas relacionadas à primeira mensalidade encontradas: {colunas_relacionadas}")
                    else:
                        st.warning(
                            "Nenhuma coluna relacionada à primeira mensalidade foi encontrada.")

                    st.warning(
                        "As colunas de primeira mensalidade não foram encontradas na planilha.")
                    return None
            else:
                st.info(
                    f"Nenhum dado encontrado para o parceiro: {parceiro_nome}")
                return None

        return None

    except Exception as e:
        st.error(f"Erro ao buscar dados de inadimplentes: {str(e)}")
        return None


def get_inadimplentes_filtrados(parceiro_nome: str, ano: int = None, mes: int = None, modalidades: List[str] = None) -> Optional[pd.DataFrame]:
    """
    Retorna dados de inadimplentes com filtros aplicados
    Modalidades permitidas: Graduação, Segunda Graduação, Tecnólogo
    """
    try:
        df_inadimplentes = get_inadimplentes_parceiro(parceiro_nome)

        if df_inadimplentes is None or df_inadimplentes.empty:
            return None

        # Aplicar filtros
        df_filtrado = df_inadimplentes.copy()

        if ano:
            df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

        if mes:
            df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

        # Filtrar apenas modalidades permitidas para inadimplentes
        modalidades_permitidas = ['Graduação',
                                  'Segunda Graduação', 'Tecnólogo']

        # Primeiro filtrar apenas as modalidades permitidas
        df_filtrado = df_filtrado[df_filtrado['Nível'].isin(
            modalidades_permitidas)]

        # Depois aplicar o filtro específico do usuário
        if modalidades and "Todas" not in modalidades:
            # Garantir que as modalidades selecionadas estão na lista permitida
            modalidades_validas = [
                m for m in modalidades if m in modalidades_permitidas]
            if modalidades_validas:
                df_filtrado = df_filtrado[df_filtrado['Nível'].isin(
                    modalidades_validas)]
            else:
                # Se nenhuma modalidade válida foi selecionada, retornar vazio
                return pd.DataFrame()

        return df_filtrado if not df_filtrado.empty else None

    except Exception as e:
        st.error(f"Erro ao filtrar dados de inadimplentes: {str(e)}")
        return None
