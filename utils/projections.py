import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import streamlit as st


class SalesProjector:
    def __init__(self):
        self.meses_nomes = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

    def prepare_historical_data(self, vendas_mensais: Dict[str, int]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados históricos para projeção"""
        meses_ordenados = []
        vendas_ordenadas = []

        # Assuming 'vendas_mensais' keys are like 'jan./2025', 'fev./2025'
        # We need to ensure we process them in month order.
        # It's better to convert the keys to datetime objects for proper sorting,
        # or rely on a fixed order if we know the input always follows it.
        # Given the fetch_data.py structure, the keys are fixed for 2025.

        # Let's rebuild this to be more robust to missing months and order them correctly
        # Assuming sales are for current year or next (2025 as per example)
        current_year = datetime.now().year
        historical_data_points = []
        for i in range(1, 13):
            month_abbr = self.meses_nomes[i].lower()[:3]
            # Use 2025 as the year, based on the example data keys in fetch_data.py
            # If the year changes, this logic needs to be updated.
            mes_key_format = f"{month_abbr}./2025"

            if mes_key_format in vendas_mensais:
                # Add month number (for X) and sales value (for y)
                historical_data_points.append(
                    {'month_num': i, 'sales': vendas_mensais[mes_key_format]})

        # Sort by month number
        historical_data_points.sort(key=lambda x: x['month_num'])

        meses_ordenados = np.array(
            [dp['month_num'] for dp in historical_data_points]).reshape(-1, 1)
        vendas_ordenadas = np.array([dp['sales']
                                    for dp in historical_data_points])

        return meses_ordenados, vendas_ordenadas

    def _calculate_positive_growth_increment(self, historical_sales: List[int]) -> float:
        """
        Calcula o incremento médio de vendas baseado apenas em progressões positivas (mês a mês).
        Retorna um valor positivo para ser adicionado a cada mês projetado.
        """
        if len(historical_sales) < 2:
            # Se não há meses suficientes para calcular progressão (apenas 0 ou 1 mês histórico),
            # usa a média simples do que existe, ou um incremento mínimo de 1.
            return np.mean(historical_sales) if historical_sales else 1.0

        positive_diffs = []
        for i in range(1, len(historical_sales)):
            diff = historical_sales[i] - historical_sales[i-1]
            if diff > 0:  # Apenas diferenças positivas são consideradas para a "progressão positiva"
                positive_diffs.append(diff)

        if positive_diffs:
            return np.mean(positive_diffs)
        else:
            # Se não houver *nenhuma* progressão positiva nos dados históricos,
            # definimos um incremento padrão para garantir que a linha suba.
            # Podemos usar uma porcentagem do último valor ou um valor fixo.
            last_val = historical_sales[-1]
            if last_val > 0:
                # Incremento de 5% do último valor, ou mínimo de 1, o que for maior
                return max(1.0, last_val * 0.05)
            return 1.0  # Incremento mínimo de 1 se o último valor for zero ou negativo

    def calculate_projections(self, vendas_mensais: Dict[str, int], meses_projecao: int = 6) -> Dict:
        """
        Calcula projeções baseadas na média de progressão positiva dos meses históricos.
        A projeção mensal parte do valor do último mês histórico.
        """
        try:
            X_hist, y_hist = self.prepare_historical_data(vendas_mensais)

            if len(y_hist) == 0:
                # Se não há dados históricos, retorna projeções zeradas
                st.warning(
                    "Não há dados históricos de vendas para projeção. Projetando 0.")
                return {
                    'projecoes_mensais': [0] * meses_projecao,
                    'projecoes_acumuladas': [0] * meses_projecao,
                    'vendas_acumuladas_atual': 0,
                    'media_mensal_atual': 0,
                    'vendas_mes_anterior': 0,
                    'mes_atual': datetime.now().month,
                    'confiabilidade': 'Baixa',
                    'meses_historicos': 0
                }

            # O último valor de venda histórico
            last_historical_sales = y_hist[-1]
            # Soma total das vendas históricas
            total_historical_sales = int(sum(y_hist))

            # Calcular o incremento médio baseado em progressões positivas
            positive_growth_increment = self._calculate_positive_growth_increment(
                y_hist.tolist())

            projecoes_mensais_list = []
            # A projeção parte do último valor histórico e adiciona o incremento
            current_projected_value = last_historical_sales

            for _ in range(meses_projecao):
                current_projected_value += positive_growth_increment
                # Garante valor não negativo e arredonda
                projecoes_mensais_list.append(
                    round(max(0, current_projected_value)))

            # Calcular projeções acumuladas
            projecoes_acumuladas_list = []
            current_cumulative_sales = total_historical_sales
            for proj_m in projecoes_mensais_list:
                current_cumulative_sales += proj_m
                projecoes_acumuladas_list.append(current_cumulative_sales)

            # Para os KPIs, use os dados históricos conforme a definição original
            media_ano = np.mean(y_hist) if len(y_hist) > 0 else 0
            mes_anterior = y_hist[-1] if len(y_hist) > 0 else 0

            return {
                'projecoes_mensais': projecoes_mensais_list,
                'projecoes_acumuladas': projecoes_acumuladas_list,
                'vendas_acumuladas_atual': total_historical_sales,
                'media_mensal_atual': round(media_ano, 1),
                'vendas_mes_anterior': int(mes_anterior),
                'mes_atual': datetime.now().month,
                'confiabilidade': self._calculate_confidence(X_hist, y_hist),
                'meses_historicos': len(y_hist)
            }

        except Exception as e:
            st.error(f"Erro ao calcular projeções: {str(e)}")
            # Fallback para uma projeção simples em caso de erro
            return self._simple_projection(vendas_mensais, meses_projecao)

    def _simple_projection(self, vendas_mensais: Dict[str, int], meses: int) -> Dict:
        """Projeção simples quando há poucos dados ou ocorre um erro."""
        valores = list(vendas_mensais.values())
        media = np.mean(valores) if valores else 0

        # Se a média for zero, e não há valores, use um incremento mínimo para projeção
        if media == 0 and len(valores) == 0:
            projecoes = [1] * meses  # Projetar 1 venda por mês como mínimo
        elif media == 0 and len(valores) > 0:
            # Se há valores históricos mas a média é 0 (e.g., todos os meses foram 0)
            projecoes = [max(0, round(media))] * meses  # Projetar 0 ou media
        else:
            projecoes = [max(0, round(media))] * meses

        vendas_acumuladas = sum(valores)

        projecoes_acumuladas = []
        acumulado = vendas_acumuladas
        for proj in projecoes:
            acumulado += proj
            projecoes_acumuladas.append(acumulado)

        return {
            'projecoes_mensais': projecoes,
            'projecoes_acumuladas': projecoes_acumuladas,
            'vendas_acumuladas_atual': int(vendas_acumuladas),
            'media_mensal_atual': round(media, 1),
            'vendas_mes_anterior': int(valores[-1]) if valores else 0,
            'mes_atual': datetime.now().month,
            'confiabilidade': 'Baixa' if len(valores) < 3 else 'Média',
            'meses_historicos': len(valores)
        }

    def _calculate_confidence(self, X: np.ndarray, y: np.ndarray) -> str:
        """Calcula nível de confiança da projeção"""
        if len(y) < 3:
            return "Baixa"
        elif len(y) < 6:
            return "Média"
        else:
            # Calcular R² para avaliar qualidade do ajuste
            # Necessário que X tenha mais de 1 dimensão
            if X.shape[0] < 2:  # Or if there's no variance
                return "Média"  # Not enough data for robust R2

            model = LinearRegression()
            try:
                model.fit(X, y)
                r2 = model.score(X, y)

                if r2 > 0.8:
                    return "Alta"
                elif r2 > 0.6:
                    return "Média"
                else:
                    return "Baixa"
            # Catch cases where fit fails (e.g., all y are same)
            except ValueError:
                return "Média"  # Fallback confidence

    def calculate_targets(self, projecoes: Dict, vendas_mensais: Dict[str, int]) -> Dict:
        """Calcula metas e comparações"""
        valores_historicos = list(vendas_mensais.values())

        # Garante que valores_historicos não esteja vazio antes de chamar max()
        if not valores_historicos:
            # Retorna um dicionário com valores padrão/zero para evitar erros
            return {
                'proximo_mes_projecao': 0,
                'falta_mes_anterior': 0,
                'falta_media_ano': 0,
                'falta_melhor_mes': 0,
                'mes_anterior_vendas': 0,
                'media_ano_vendas': 0,
                'melhor_mes_vendas': 0
            }

        # Próximo mês (a primeira projeção mensal)
        proximo_mes_proj = projecoes['projecoes_mensais'][0] if projecoes['projecoes_mensais'] else 0

        # Para bater o mês anterior
        mes_anterior = projecoes['vendas_mes_anterior']
        falta_mes_anterior = mes_anterior - proximo_mes_proj

        # Para bater a média do ano
        media_ano = projecoes['media_mensal_atual']
        falta_media_ano = media_ano - proximo_mes_proj

        # Para bater o melhor mês
        melhor_mes = max(valores_historicos)
        falta_melhor_mes = melhor_mes - proximo_mes_proj

        return {
            'proximo_mes_projecao': proximo_mes_proj,
            'falta_mes_anterior': round(falta_mes_anterior),
            'falta_media_ano': round(falta_media_ano),
            'falta_melhor_mes': round(falta_melhor_mes),
            'mes_anterior_vendas': mes_anterior,
            'media_ano_vendas': round(media_ano, 1),
            'melhor_mes_vendas': melhor_mes
        }
