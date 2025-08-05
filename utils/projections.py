import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import streamlit as st


class SalesProjector:
    def __init__(self):
        self.meses_nomes = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

    def prepare_historical_data(self, vendas_mensais: Dict[str, int]) -> Tuple[List[int], List[int]]:
        """Prepara dados históricos para projeção"""
        meses_ordenados = []
        vendas_ordenadas = []

        # Processar dados mensais na ordem correta
        for i in range(1, 13):
            month_abbr = self.meses_nomes[i].lower()[:3]
            mes_key = f"{month_abbr}./2025"

            if mes_key in vendas_mensais and vendas_mensais[mes_key] > 0:
                meses_ordenados.append(i)
                vendas_ordenadas.append(vendas_mensais[mes_key])

        return meses_ordenados, vendas_ordenadas

    def _calculate_positive_growth_increment(self, historical_sales: List[int]) -> float:
        """
        Calcula o incremento médio de vendas baseado apenas em progressões positivas
        """
        if len(historical_sales) < 2:
            # Se há apenas 1 mês ou menos, usar 10% do valor como incremento
            return max(1.0, historical_sales[0] * 0.1) if historical_sales else 1.0

        positive_diffs = []
        for i in range(1, len(historical_sales)):
            diff = historical_sales[i] - historical_sales[i-1]
            if diff > 0:  # Apenas progressões positivas
                positive_diffs.append(diff)

        if positive_diffs:
            return np.mean(positive_diffs)
        else:
            # Se não há progressão positiva, usar 5% do último valor
            last_val = historical_sales[-1]
            return max(1.0, last_val * 0.05) if last_val > 0 else 1.0

    def get_previous_month_sales(self, vendas_mensais: Dict[str, int]) -> int:
        """Identifica as vendas do mês anterior ao atual"""
        mes_atual = datetime.now().month

        # Procurar o mês anterior
        for mes_num in range(mes_atual - 1, 0, -1):  # Do mês anterior para janeiro
            month_abbr = self.meses_nomes[mes_num].lower()[:3]
            mes_key = f"{month_abbr}./2025"

            if mes_key in vendas_mensais and vendas_mensais[mes_key] > 0:
                return vendas_mensais[mes_key]

        # Se não encontrou, pegar o último mês com vendas
        for i in range(12, 0, -1):
            month_abbr = self.meses_nomes[i].lower()[:3]
            mes_key = f"{month_abbr}./2025"

            if mes_key in vendas_mensais and vendas_mensais[mes_key] > 0:
                return vendas_mensais[mes_key]

        return 0

    def calculate_projections(self, vendas_mensais: Dict[str, int], meses_projecao: int = 6) -> Dict:
        """
        Calcula projeções baseadas na média de progressão positiva
        """
        try:
            meses_hist, vendas_hist = self.prepare_historical_data(
                vendas_mensais)

            if len(vendas_hist) == 0:
                return {
                    'projecoes_mensais': [1] * meses_projecao,
                    'projecoes_acumuladas': list(range(1, meses_projecao + 1)),
                    'vendas_acumuladas_atual': 0,
                    'media_mensal_atual': 0,
                    'vendas_mes_anterior': 0,
                    'mes_atual': datetime.now().month,
                    'confiabilidade': 'Baixa',
                    'meses_historicos': 0
                }

            # Último valor histórico
            last_historical_sales = vendas_hist[-1]
            total_historical_sales = sum(vendas_hist)

            # Calcular incremento baseado em progressão positiva
            positive_growth_increment = self._calculate_positive_growth_increment(
                vendas_hist)

            # Projeções mensais - cada mês cresce baseado no incremento
            projecoes_mensais_list = []
            current_projected_value = last_historical_sales

            for i in range(meses_projecao):
                current_projected_value += positive_growth_increment
                projecoes_mensais_list.append(
                    round(max(0, current_projected_value)))

            # Projeções acumuladas
            projecoes_acumuladas_list = []
            current_cumulative = total_historical_sales

            for proj_mensal in projecoes_mensais_list:
                # Somar a projeção mensal ao acumulado
                # Mas a projeção mensal já é o valor total do mês, não o incremento
                # Então precisamos somar apenas o incremento real
                incremento_mensal = proj_mensal - (projecoes_mensais_list[projecoes_mensais_list.index(
                    proj_mensal) - 1] if projecoes_mensais_list.index(proj_mensal) > 0 else last_historical_sales)
                current_cumulative += incremento_mensal
                projecoes_acumuladas_list.append(current_cumulative)

            # Recalcular corretamente as projeções acumuladas
            projecoes_acumuladas_list = []
            current_cumulative = total_historical_sales

            for i, proj_mensal in enumerate(projecoes_mensais_list):
                if i == 0:
                    # Primeiro mês: somar a diferença entre a projeção e o último histórico
                    incremento = proj_mensal - last_historical_sales
                else:
                    # Meses seguintes: somar a diferença entre esta projeção e a anterior
                    incremento = proj_mensal - projecoes_mensais_list[i-1]

                current_cumulative += incremento
                projecoes_acumuladas_list.append(current_cumulative)

            # Estatísticas
            media_ano = np.mean(vendas_hist)
            mes_anterior_vendas = self.get_previous_month_sales(vendas_mensais)

            return {
                'projecoes_mensais': projecoes_mensais_list,
                'projecoes_acumuladas': projecoes_acumuladas_list,
                'vendas_acumuladas_atual': total_historical_sales,
                'media_mensal_atual': round(media_ano, 1),
                'vendas_mes_anterior': mes_anterior_vendas,
                'mes_atual': datetime.now().month,
                'confiabilidade': self._calculate_confidence_simple(vendas_hist),
                'meses_historicos': len(vendas_hist)
            }

        except Exception as e:
            st.error(f"Erro ao calcular projeções: {str(e)}")
            return self._simple_projection(vendas_mensais, meses_projecao)

    def _calculate_confidence_simple(self, vendas_hist: List[int]) -> str:
        """Calcula confiança baseado na quantidade e variabilidade dos dados"""
        if len(vendas_hist) < 3:
            return "Baixa"
        elif len(vendas_hist) < 6:
            return "Média"
        else:
            # Verificar consistência dos dados
            std_dev = np.std(vendas_hist)
            mean_val = np.mean(vendas_hist)
            cv = std_dev / mean_val if mean_val > 0 else 1

            if cv < 0.2:
                return "Alta"
            elif cv < 0.4:
                return "Média"
            else:
                return "Baixa"

    def _simple_projection(self, vendas_mensais: Dict[str, int], meses: int) -> Dict:
        """Projeção simples para fallback"""
        valores = list(vendas_mensais.values())
        valores_positivos = [v for v in valores if v > 0]

        if not valores_positivos:
            media = 1
        else:
            media = np.mean(valores_positivos)

        # Projeção com crescimento de 5% ao mês
        projecoes = []
        valor_base = media
        for i in range(meses):
            valor_base *= 1.05  # Crescimento de 5%
            projecoes.append(round(valor_base))

        vendas_acumuladas = sum(valores)

        projecoes_acumuladas = []
        acumulado = vendas_acumuladas
        for proj in projecoes:
            acumulado += proj
            projecoes_acumuladas.append(acumulado)

        mes_anterior_vendas = self.get_previous_month_sales(vendas_mensais)

        return {
            'projecoes_mensais': projecoes,
            'projecoes_acumuladas': projecoes_acumuladas,
            'vendas_acumuladas_atual': int(vendas_acumuladas),
            'media_mensal_atual': round(media, 1),
            'vendas_mes_anterior': mes_anterior_vendas,
            'mes_atual': datetime.now().month,
            'confiabilidade': 'Baixa' if len(valores_positivos) < 3 else 'Média',
            'meses_historicos': len(valores_positivos)
        }

    def calculate_targets(self, projecoes: Dict, vendas_mensais: Dict[str, int]) -> Dict:
        """Calcula metas e comparações"""
        valores_historicos = [v for v in vendas_mensais.values() if v > 0]

        if not valores_historicos:
            return {
                'proximo_mes_projecao': 0,
                'falta_mes_anterior': 0,
                'falta_media_ano': 0,
                'falta_melhor_mes': 0,
                'mes_anterior_vendas': 0,
                'media_ano_vendas': 0,
                'melhor_mes_vendas': 0
            }

        # Próximo mês projetado
        proximo_mes_proj = projecoes['projecoes_mensais'][0] if projecoes['projecoes_mensais'] else 0

        # Mês anterior real
        mes_anterior = projecoes['vendas_mes_anterior']

        # Média do ano
        media_ano = projecoes['media_mensal_atual']

        # Melhor mês histórico
        melhor_mes = max(valores_historicos)

        # Calcular o que falta (valores positivos = falta, negativos = superou)
        falta_mes_anterior = max(0, mes_anterior - proximo_mes_proj)
        falta_media_ano = max(0, media_ano - proximo_mes_proj)
        falta_melhor_mes = max(0, melhor_mes - proximo_mes_proj)

        return {
            'proximo_mes_projecao': int(proximo_mes_proj),
            'falta_mes_anterior': int(falta_mes_anterior),
            'falta_media_ano': int(falta_media_ano),
            'falta_melhor_mes': int(falta_melhor_mes),
            'mes_anterior_vendas': int(mes_anterior),
            'media_ano_vendas': round(media_ano, 1),
            'melhor_mes_vendas': int(melhor_mes)
        }
