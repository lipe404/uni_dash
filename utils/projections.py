import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import streamlit as st
from sklearn.linear_model import LinearRegression
# Certifique-se de ter statsmodels instalado (pip install statsmodels)
from statsmodels.tsa.arima.model import ARIMA


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
        # Filtrar apenas vendas com valores maiores que 0
        for i in range(1, 13):
            month_abbr = self.meses_nomes[i].lower()[:3]
            mes_key = f"{month_abbr}./2025"  # Assumindo ano fixo por enquanto

            if mes_key in vendas_mensais and vendas_mensais[mes_key] > 0:
                meses_ordenados.append(i)
                vendas_ordenadas.append(vendas_mensais[mes_key])

        return meses_ordenados, vendas_ordenadas

    def _calculate_average_monthly_change(self, historical_sales: List[int]) -> Tuple[float, float]:
        """
        Calcula a média de TODAS as variações mensais e seu desvio padrão.
        """
        if len(historical_sales) < 2:
            return (max(1.0, historical_sales[0] * 0.05) if historical_sales else 1.0, 0.0)

        all_diffs = []
        for i in range(1, len(historical_sales)):
            diff = historical_sales[i] - historical_sales[i-1]
            all_diffs.append(diff)

        if all_diffs:
            average_change = np.mean(all_diffs)
            std_dev_change = np.std(all_diffs)

            # Limite inferior para a média de mudança (evita quedas drásticas irreais)
            if average_change < -historical_sales[-1] * 0.5:
                # Max 10% de queda por mês
                average_change = -historical_sales[-1] * 0.1

            return average_change, std_dev_change
        else:
            last_val = historical_sales[-1]
            return (max(1.0, last_val * 0.01) if last_val > 0 else 1.0, 0.0)

    def _project_base(self, last_value: float, increment: float, meses: int, std_dev: float = 0.0) -> Tuple[List[float], List[float], List[float]]:
        """
        Base para projeções mensais com cone de incerteza.
        Retorna projeção média, limite inferior e limite superior.
        """
        projecoes = []
        lower_bounds = []
        upper_bounds = []
        current_val = last_value

        for i in range(meses):
            current_val += increment

            # Adicionar incerteza (ex: 1.96 * desvio padrão para 95% de confiança)
            # O fator de incerteza aumenta com o tempo (raiz quadrada do número de passos)
            # Ajuste o multiplicador (1.5) conforme a amplitude desejada
            uncertainty = std_dev * np.sqrt(i + 1) * 1.5

            avg_proj = max(0, round(current_val))
            lower_proj = max(0, round(current_val - uncertainty))
            upper_proj = max(0, round(current_val + uncertainty))

            projecoes.append(avg_proj)
            lower_bounds.append(lower_proj)
            upper_bounds.append(upper_proj)

        return projecoes, lower_bounds, upper_bounds

    def _linear_regression_projection(self, meses_hist: List[int], vendas_hist: List[int], meses_projecao: int) -> Tuple[List[float], List[float], List[float]]:
        if len(meses_hist) < 2:
            return self._project_base(vendas_hist[-1] if vendas_hist else 0, 1.0, meses_projecao)

        X = np.array(meses_hist).reshape(-1, 1)
        y = np.array(vendas_hist)

        model = LinearRegression()
        model.fit(X, y)

        last_month_num = meses_hist[-1]
        future_months = np.array([[last_month_num + i + 1]
                                 for i in range(meses_projecao)])

        predictions = model.predict(future_months)

        # Calcular resíduos para desvio padrão
        if len(meses_hist) > 1:
            residuals = y - model.predict(X)
            std_dev_residuals = np.std(residuals)
        else:
            std_dev_residuals = 0.0

        # Baseado na tendência
        return self._project_base(vendas_hist[-1], 0.0, meses_projecao, std_dev_residuals)
        # Ou simplesmente retornar predictions e calcular bounds externamente se for preferível não usar _project_base
        # Aqui, vamos usar a _project_base para manter a consistência do cone

    def _moving_average_projection(self, vendas_hist: List[int], meses_projecao: int, window: int = 3) -> Tuple[List[float], List[float], List[float]]:
        if not vendas_hist:
            return self._project_base(0, 1.0, meses_projecao)

        if len(vendas_hist) < window:
            ma = np.mean(vendas_hist)
        else:
            ma = np.mean(vendas_hist[-window:])

        # Estimar desvio padrão dos últimos valores
        std_dev = np.std(vendas_hist[-window:]) if len(
            vendas_hist) >= window else np.std(vendas_hist) if vendas_hist else 0.0

        return self._project_base(vendas_hist[-1], ma - vendas_hist[-1] if vendas_hist else ma, meses_projecao, std_dev)

    def _arima_projection(self, vendas_hist: List[int], meses_projecao: int) -> Tuple[List[float], List[float], List[float]]:
        if len(vendas_hist) < 5:  # ARIMA precisa de mais dados
            return self._project_base(vendas_hist[-1] if vendas_hist else 0, 1.0, meses_projecao)

        try:
            # Tentar um modelo ARIMA simples (p,d,q) = (1,1,0) ou (1,0,0)
            # 1,1,0: Considera uma diferença para tornar a série estacionária e um termo AR.
            # 1,0,0: Apenas um termo AR.
            # Se for muito ruidoso, pode usar (0,1,1) ou (1,1,1). Ajustar conforme o comportamento dos dados.
            # Pode ser (1,0,0) se os dados já forem estacionários
            model = ARIMA(vendas_hist, order=(1, 1, 0))
            model_fit = model.fit()

            forecast_results = model_fit.get_forecast(steps=meses_projecao)
            predictions = forecast_results.predicted_mean.tolist()
            conf_int = forecast_results.conf_int(
                alpha=0.05)  # 95% confidence interval

            lower_bounds = conf_int[:, 0].tolist()
            upper_bounds = conf_int[:, 1].tolist()

            # Garantir que as projeções não sejam negativas
            predictions = [max(0, round(p)) for p in predictions]
            lower_bounds = [max(0, round(l)) for l in lower_bounds]
            upper_bounds = [max(0, round(u)) for u in upper_bounds]

            return predictions, lower_bounds, upper_bounds
        except Exception as e:
            st.warning(f"Erro no modelo ARIMA, utilizando fallback: {e}")
            return self._project_base(vendas_hist[-1] if vendas_hist else 0, 1.0, meses_projecao)

    def _calculate_cumulative_projections(self, historical_sales: List[int], meses_projecao: int, monthly_projections: List[float], lower_bounds_monthly: List[float], upper_bounds_monthly: List[float]) -> Tuple[List[int], List[int], List[int]]:
        """
        Calcula projeções acumuladas baseadas nas projeções mensais.
        O acumulado SEMPRE cresce, nunca diminui.
        """
        total_atual = sum(historical_sales) if historical_sales else 0

        projecoes_acumuladas = []
        lower_bounds_acumuladas = []
        upper_bounds_acumuladas = []

        current_cumulative_avg = total_atual
        current_cumulative_lower = total_atual
        current_cumulative_upper = total_atual

        for i in range(meses_projecao):
            # Usar as projeções mensais para calcular o acumulado
            # Garante que o acumulado sempre aumente com um mínimo de 1 venda
            current_cumulative_avg += max(1, monthly_projections[i])
            current_cumulative_lower += max(1, lower_bounds_monthly[i])
            current_cumulative_upper += max(1, upper_bounds_monthly[i])

            projecoes_acumuladas.append(round(current_cumulative_avg))
            lower_bounds_acumuladas.append(round(current_cumulative_lower))
            upper_bounds_acumuladas.append(round(current_cumulative_upper))

        return projecoes_acumuladas, lower_bounds_acumuladas, upper_bounds_acumuladas

    def get_previous_month_sales(self, vendas_mensais: Dict[str, int]) -> int:
        """Identifica as vendas do mês anterior ao atual"""
        mes_atual = datetime.now().month
        current_year = datetime.now().year  # Assume o ano atual para o cálculo

        # Cria uma lista de meses do ano para iterar de forma ordenada
        ordered_months_keys = []
        for i in range(1, mes_atual):  # Vai do Jan até o mês anterior ao atual
            month_abbr = self.meses_nomes[i].lower()[:3]
            ordered_months_keys.append(f"{month_abbr}./{current_year}")

        # Busca o último mês com vendas > 0 na ordem correta
        last_month_sales = 0
        for mes_key in ordered_months_keys[::-1]:  # Itera de trás para frente
            if mes_key in vendas_mensais and vendas_mensais[mes_key] > 0:
                last_month_sales = vendas_mensais[mes_key]
                break

        return last_month_sales

    def calculate_projections(self, vendas_mensais: Dict[str, int], meses_projecao: int = 6,
                              model_type: str = "Média de Variação",
                              growth_factor: Optional[float] = None) -> Dict:
        """
        Calcula projeções mensais e acumuladas usando o modelo selecionado.
        Pode aplicar um fator de crescimento.
        """
        try:
            meses_hist_nums, vendas_hist = self.prepare_historical_data(
                vendas_mensais)

            if len(vendas_hist) == 0:
                # Retorna valores padrão caso não haja histórico de vendas
                default_proj = [1] * meses_projecao
                default_cum_proj = list(range(1, meses_projecao + 1))
                return {
                    'projecoes_mensais': default_proj,
                    'lower_bounds_mensais': default_proj,
                    'upper_bounds_mensais': default_proj,
                    'projecoes_acumuladas': default_cum_proj,
                    'lower_bounds_acumuladas': default_cum_proj,
                    'upper_bounds_acumuladas': default_cum_proj,
                    'vendas_acumuladas_atual': 0,
                    'media_mensal_atual': 0,
                    'vendas_mes_anterior': 0,
                    'mes_atual': datetime.now().month,
                    'confiabilidade': 'Baixa',
                    'meses_historicos': 0
                }

            last_historical_sales = vendas_hist[-1]
            total_historical_sales = sum(vendas_hist)

            # Escolha do modelo de projeção mensal
            if model_type == "Média de Variação":
                avg_change, std_dev_change = self._calculate_average_monthly_change(
                    vendas_hist)
                projecoes_mensais, lower_bounds_mensais, upper_bounds_mensais = \
                    self._project_base(
                        last_historical_sales, avg_change, meses_projecao, std_dev_change)
            elif model_type == "Regressão Linear":
                projecoes_mensais, lower_bounds_mensais, upper_bounds_mensais = \
                    self._linear_regression_projection(
                        meses_hist_nums, vendas_hist, meses_projecao)
            elif model_type == "Média Móvel":
                projecoes_mensais, lower_bounds_mensais, upper_bounds_mensais = \
                    self._moving_average_projection(
                        vendas_hist, meses_projecao)
            elif model_type == "ARIMA":
                projecoes_mensais, lower_bounds_mensais, upper_bounds_mensais = \
                    self._arima_projection(vendas_hist, meses_projecao)
            else:  # Fallback para média de variação
                avg_change, std_dev_change = self._calculate_average_monthly_change(
                    vendas_hist)
                projecoes_mensais, lower_bounds_mensais, upper_bounds_mensais = \
                    self._project_base(
                        last_historical_sales, avg_change, meses_projecao, std_dev_change)

            # Aplicar fator de crescimento do cenário "E se..."
            if growth_factor is not None:
                factor = 1 + (growth_factor / 100)
                projecoes_mensais = [round(p * factor)
                                     for p in projecoes_mensais]
                lower_bounds_mensais = [round(l * factor)
                                        for l in lower_bounds_mensais]
                upper_bounds_mensais = [round(u * factor)
                                        for u in upper_bounds_mensais]

            # Recalcular projeções acumuladas com base nas projeções mensais (média e bounds)
            projecoes_acumuladas, lower_bounds_acumuladas, upper_bounds_acumuladas = \
                self._calculate_cumulative_projections(
                    vendas_hist, meses_projecao, projecoes_mensais, lower_bounds_mensais, upper_bounds_mensais)

            # Estatísticas
            media_ano = np.mean(vendas_hist)
            mes_anterior_vendas = self.get_previous_month_sales(vendas_mensais)

            return {
                'projecoes_mensais': projecoes_mensais,
                'lower_bounds_mensais': lower_bounds_mensais,
                'upper_bounds_mensais': upper_bounds_mensais,
                'projecoes_acumuladas': projecoes_acumuladas,
                'lower_bounds_acumuladas': lower_bounds_acumuladas,
                'upper_bounds_acumuladas': upper_bounds_acumuladas,
                'vendas_acumuladas_atual': total_historical_sales,
                'media_mensal_atual': round(media_ano, 1),
                'vendas_mes_anterior': mes_anterior_vendas,
                'mes_atual': datetime.now().month,
                'confiabilidade': self._calculate_confidence_simple(vendas_hist),
                'meses_historicos': len(vendas_hist)
            }

        except Exception as e:
            st.error(f"Erro ao calcular projeções: {str(e)}")
            # Fallback para uma projeção simples em caso de erro
            return self._simple_projection(vendas_mensais, meses_projecao)

    def _calculate_confidence_simple(self, vendas_hist: List[int]) -> str:
        """Calcula confiança baseado na quantidade e variabilidade dos dados"""
        if len(vendas_hist) < 3:
            return "Baixa"
        elif len(vendas_hist) < 6:
            return "Média"
        else:
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
        """Projeção simples para fallback quando ocorre erro ou não há dados suficientes"""
        valores = [v for v in vendas_mensais.values() if v > 0]

        media = np.mean(valores) if valores else 1

        # Incremento padrão se não houver dados suficientes ou ocorrências significativas
        if len(valores) < 2:
            tendencia = media * 0.05
        else:
            tendencia = (valores[-1] - valores[0]) / \
                len(valores) if len(valores) > 1 else media * 0.05

        projecoes = []
        valor_base = valores[-1] if valores else media
        for i in range(meses):
            valor_base += tendencia
            projecoes.append(round(max(1, valor_base)))

        # Para o fallback, os limites superior e inferior serão a própria projeção para simplicidade
        lower_bounds = [p for p in projecoes]
        upper_bounds = [p for p in projecoes]

        vendas_acumuladas_atual = sum(valores) if valores else 0

        projecoes_acumuladas, lower_bounds_acumuladas, upper_bounds_acumuladas = \
            self._calculate_cumulative_projections(
                valores, meses, projecoes, lower_bounds, upper_bounds)

        mes_anterior_vendas = self.get_previous_month_sales(vendas_mensais)

        return {
            'projecoes_mensais': projecoes,
            'lower_bounds_mensais': lower_bounds,
            'upper_bounds_mensais': upper_bounds,
            'projecoes_acumuladas': projecoes_acumuladas,
            'lower_bounds_acumuladas': lower_bounds_acumuladas,
            'upper_bounds_acumuladas': upper_bounds_acumuladas,
            'vendas_acumuladas_atual': int(vendas_acumuladas_atual),
            'media_mensal_atual': round(media, 1),
            'vendas_mes_anterior': mes_anterior_vendas,
            'mes_atual': datetime.now().month,
            'confiabilidade': 'Baixa',
            'meses_historicos': len(valores)
        }

    def calculate_targets(self, projecoes: Dict, vendas_mensais: Dict[str, int]) -> Dict:
        """Calcula metas e comparações"""
        # Apenas valores históricos > 0
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

        proximo_mes_proj = projecoes['projecoes_mensais'][0] if projecoes['projecoes_mensais'] else 0
        mes_anterior = projecoes['vendas_mes_anterior']
        media_ano = projecoes['media_mensal_atual']
        melhor_mes = max(valores_historicos)

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
