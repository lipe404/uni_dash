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

    def _calculate_average_monthly_change(self, historical_sales: List[int]) -> float:
        """
        Calcula a média de TODAS as variações mensais (positivas e negativas).
        Isso torna a projeção mais realista, considerando tanto crescimentos quanto declínios.
        """
        if len(historical_sales) < 2:
            # Se há apenas 1 mês ou menos, usar 5% do valor como incremento padrão
            return max(1.0, historical_sales[0] * 0.05) if historical_sales else 1.0

        all_diffs = []
        for i in range(1, len(historical_sales)):
            diff = historical_sales[i] - historical_sales[i-1]
            # Incluir TODAS as diferenças (positivas e negativas)
            all_diffs.append(diff)

        if all_diffs:
            average_change = np.mean(all_diffs)

            # Se a média for muito negativa, aplicar um limite mínimo
            # para evitar projeções que caiam para zero ou negativo
            # Limite: não mais que 50% de queda
            if average_change < -historical_sales[-1] * 0.5:
                # Máximo 10% de queda por mês
                average_change = -historical_sales[-1] * 0.1

            return average_change
        else:
            # Fallback: crescimento mínimo de 1% do último valor
            last_val = historical_sales[-1]
            return max(1.0, last_val * 0.01) if last_val > 0 else 1.0

    def _calculate_cumulative_projections(self, historical_sales: List[int], meses_projecao: int) -> List[int]:
        """
        Calcula projeções acumuladas baseadas na média mensal histórica.
        O acumulado SEMPRE cresce, nunca diminui.
        """
        if not historical_sales:
            # Se não há dados históricos, usar crescimento padrão
            base_monthly = 5  # 5 vendas por mês como padrão
            total_atual = 0
        else:
            # Calcular média mensal dos dados históricos
            media_mensal = np.mean(historical_sales)
            total_atual = sum(historical_sales)

            # Se a média for muito baixa, aplicar um mínimo
            base_monthly = max(1, media_mensal)

        # Calcular projeções acumuladas
        projecoes_acumuladas = []
        acumulado_atual = total_atual

        for i in range(meses_projecao):
            # Cada mês adiciona pelo menos a média mensal ao acumulado
            # Pode incluir um pequeno fator de crescimento baseado na tendência
            if len(historical_sales) >= 2:
                # Calcular tendência de crescimento da média mensal
                primeiro_mes = historical_sales[0]
                ultimo_mes = historical_sales[-1]
                crescimento_percentual = (
                    ultimo_mes - primeiro_mes) / primeiro_mes if primeiro_mes > 0 else 0

                # Aplicar crescimento gradual (limitado a ±20% por mês)
                fator_crescimento = max(-0.2, min(0.2,
                                        crescimento_percentual / len(historical_sales)))
                incremento_mensal = base_monthly * (1 + fator_crescimento)
            else:
                # Sem dados suficientes, usar média simples
                incremento_mensal = base_monthly

            # Garantir que o incremento seja sempre positivo (acumulado sempre cresce)
            incremento_mensal = max(1, incremento_mensal)

            acumulado_atual += incremento_mensal
            projecoes_acumuladas.append(round(acumulado_atual))

        return projecoes_acumuladas

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
        Calcula projeções mensais e acumuladas
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

            # Calcular incremento baseado na média de TODAS as variações (para projeções mensais)
            average_monthly_change = self._calculate_average_monthly_change(
                vendas_hist)

            # Projeções mensais - cada mês varia baseado na média de mudanças
            projecoes_mensais_list = []
            current_projected_value = last_historical_sales

            for i in range(meses_projecao):
                current_projected_value += average_monthly_change
                # Garantir que as vendas projetadas não fiquem negativas
                projecoes_mensais_list.append(
                    round(max(0, current_projected_value)))

            # Projeções acumuladas - usando método específico que SEMPRE cresce
            projecoes_acumuladas_list = self._calculate_cumulative_projections(
                vendas_hist, meses_projecao)

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

        # Projeção com variação baseada na tendência dos dados
        projecoes = []
        if len(valores_positivos) >= 2:
            # Calcular tendência simples
            tendencia = (
                valores_positivos[-1] - valores_positivos[0]) / len(valores_positivos)
        else:
            tendencia = media * 0.02  # 2% de crescimento padrão

        valor_base = media
        for i in range(meses):
            valor_base += tendencia
            projecoes.append(round(max(1, valor_base)))  # Mínimo de 1 venda

        vendas_acumuladas = sum(valores)

        # Projeções acumuladas usando método específico
        projecoes_acumuladas = self._calculate_cumulative_projections(
            valores_positivos, meses)

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
