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

        for i in range(1, 13):
            mes_key = f"{self.meses_nomes[i].lower()[:3]}./2025"
            if mes_key in vendas_mensais:
                meses_ordenados.append(i)
                vendas_ordenadas.append(vendas_mensais[mes_key])

        return np.array(meses_ordenados).reshape(-1, 1), np.array(vendas_ordenadas)

    def calculate_projections(self, vendas_mensais: Dict[str, int], meses_projecao: int = 6) -> Dict:
        """Calcula projeções usando múltiplos métodos"""
        try:
            X, y = self.prepare_historical_data(vendas_mensais)

            if len(X) < 3:  # Precisa de pelo menos 3 pontos
                return self._simple_projection(vendas_mensais, meses_projecao)

            # Método 1: Regressão Linear
            linear_proj = self._linear_regression_projection(
                X, y, meses_projecao)

            # Método 2: Média Móvel
            moving_avg_proj = self._moving_average_projection(
                y, meses_projecao)

            # Método 3: Tendência Sazonal
            seasonal_proj = self._seasonal_projection(
                vendas_mensais, meses_projecao)

            # Combinar métodos (média ponderada)
            final_projections = []
            for i in range(meses_projecao):
                combined = (
                    linear_proj[i] * 0.4 +
                    moving_avg_proj[i] * 0.3 +
                    seasonal_proj[i] * 0.3
                )
                final_projections.append(max(0, round(combined)))

            # Calcular acumulado atual
            vendas_acumuladas = sum(y)

            # Projeções acumuladas
            projecoes_acumuladas = []
            acumulado_atual = vendas_acumuladas
            for proj in final_projections:
                acumulado_atual += proj
                projecoes_acumuladas.append(acumulado_atual)

            # Calcular mês atual
            mes_atual = datetime.now().month

            # Estatísticas de comparação
            media_ano = np.mean(y) if len(y) > 0 else 0
            mes_anterior = y[-1] if len(y) > 0 else 0

            return {
                'projecoes_mensais': final_projections,
                'projecoes_acumuladas': projecoes_acumuladas,
                'vendas_acumuladas_atual': int(vendas_acumuladas),
                'media_mensal_atual': round(media_ano, 1),
                'vendas_mes_anterior': int(mes_anterior),
                'mes_atual': mes_atual,
                'confiabilidade': self._calculate_confidence(X, y),
                'meses_historicos': len(y)
            }

        except Exception as e:
            st.error(f"Erro ao calcular projeções: {str(e)}")
            return self._simple_projection(vendas_mensais, meses_projecao)

    def _linear_regression_projection(self, X: np.ndarray, y: np.ndarray, meses: int) -> List[float]:
        """Projeção usando regressão linear"""
        model = LinearRegression()
        model.fit(X, y)

        ultimo_mes = X[-1][0] if len(X) > 0 else datetime.now().month
        futuros_meses = np.array([[ultimo_mes + i + 1] for i in range(meses)])

        return model.predict(futuros_meses).tolist()

    def _moving_average_projection(self, y: np.ndarray, meses: int) -> List[float]:
        """Projeção usando média móvel"""
        if len(y) >= 3:
            media_recente = np.mean(y[-3:])  # Média dos últimos 3 meses
        else:
            media_recente = np.mean(y)

        # Aplicar pequena tendência baseada na evolução recente
        if len(y) >= 2:
            tendencia = (y[-1] - y[0]) / len(y)
        else:
            tendencia = 0

        projecoes = []
        for i in range(meses):
            proj = media_recente + (tendencia * (i + 1))
            projecoes.append(max(0, proj))

        return projecoes

    def _seasonal_projection(self, vendas_mensais: Dict[str, int], meses: int) -> List[float]:
        """Projeção considerando sazonalidade"""
        # Calcular média geral
        valores = list(vendas_mensais.values())
        media_geral = np.mean(valores) if valores else 0

        # Fatores sazonais hipotéticos (baseados em padrões educacionais)
        fatores_sazonais = {
            1: 1.1,   # Janeiro - início do ano
            2: 1.2,   # Fevereiro - matrículas
            3: 1.0,   # Março
            4: 0.9,   # Abril
            5: 0.8,   # Maio
            6: 0.7,   # Junho
            7: 0.6,   # Julho - férias
            8: 1.3,   # Agosto - volta às aulas
            9: 1.1,   # Setembro
            10: 1.0,  # Outubro
            11: 0.9,  # Novembro
            12: 0.8   # Dezembro - férias
        }

        mes_atual = datetime.now().month
        projecoes = []

        for i in range(meses):
            mes_futuro = ((mes_atual + i) % 12) + 1
            fator = fatores_sazonais.get(mes_futuro, 1.0)
            proj = media_geral * fator
            projecoes.append(max(0, proj))

        return projecoes

    def _simple_projection(self, vendas_mensais: Dict[str, int], meses: int) -> Dict:
        """Projeção simples quando há poucos dados"""
        valores = list(vendas_mensais.values())
        media = np.mean(valores) if valores else 0

        projecoes = [max(0, round(media)) for _ in range(meses)]
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
            model = LinearRegression()
            model.fit(X, y)
            r2 = model.score(X, y)

            if r2 > 0.8:
                return "Alta"
            elif r2 > 0.6:
                return "Média"
            else:
                return "Baixa"

    def calculate_targets(self, projecoes: Dict, vendas_mensais: Dict[str, int]) -> Dict:
        """Calcula metas e comparações"""
        valores_historicos = list(vendas_mensais.values())

        # Próximo mês
        proximo_mes_proj = projecoes['projecoes_mensais'][0] if projecoes['projecoes_mensais'] else 0

        # Para bater o mês anterior
        mes_anterior = projecoes['vendas_mes_anterior']
        falta_mes_anterior = max(0, mes_anterior - proximo_mes_proj)

        # Para bater a média do ano
        media_ano = projecoes['media_mensal_atual']
        falta_media_ano = max(0, media_ano - proximo_mes_proj)

        # Para bater o melhor mês
        melhor_mes = max(valores_historicos) if valores_historicos else 0
        falta_melhor_mes = max(0, melhor_mes - proximo_mes_proj)

        return {
            'proximo_mes_projecao': proximo_mes_proj,
            'falta_mes_anterior': round(falta_mes_anterior),
            'falta_media_ano': round(falta_media_ano),
            'falta_melhor_mes': round(falta_melhor_mes),
            'mes_anterior_vendas': mes_anterior,
            'media_ano_vendas': round(media_ano, 1),
            'melhor_mes_vendas': melhor_mes
        }
