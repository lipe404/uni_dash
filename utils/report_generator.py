import pandas as pd
import streamlit as st
from datetime import datetime
import io
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import plotly.graph_objects as go
import plotly.io as pio
from data.fetch_data import get_parceiro_vendas_detalhadas, fetch_vendas_publicas


class ReportGenerator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_filtered_sales_data(self, parceiro_nome: str, ano: int = None, mes: int = None, modalidades: List[str] = None) -> pd.DataFrame:
        """Busca dados de vendas filtrados"""
        try:
            df_vendas = get_parceiro_vendas_detalhadas(parceiro_nome)

            if df_vendas is None or df_vendas.empty:
                return pd.DataFrame()

            # Aplicar filtros
            df_filtrado = df_vendas.copy()

            if ano:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.year == ano]

            if mes:
                df_filtrado = df_filtrado[df_filtrado['Dt Pagto'].dt.month == mes]

            if modalidades and "Todas" not in modalidades:
                df_filtrado = df_filtrado[df_filtrado['Nível'].isin(
                    modalidades)]

            return df_filtrado

        except Exception as e:
            st.error(f"Erro ao buscar dados filtrados: {str(e)}")
            return pd.DataFrame()

    def generate_summary_report_excel(self, parceiro_nome: str, ano: int = None, mes: int = None, modalidades: List[str] = None) -> bytes:
        """Gera relatório resumido em Excel"""
        try:
            df_vendas = self.get_filtered_sales_data(
                parceiro_nome, ano, mes, modalidades)

            if df_vendas.empty:
                st.warning(
                    "Nenhum dado encontrado para os filtros selecionados.")
                return b""

            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book

                # Formatos
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#667eea',
                    'font_color': 'white',
                    'border': 1
                })

                number_format = workbook.add_format({'num_format': '#,##0'})

                # Aba 1: Resumo Geral
                resumo_data = {
                    'Métrica': [
                        'Total de Vendas',
                        'Total de Matrículas',
                        'Modalidades Diferentes',
                        'Cursos Diferentes',
                        'Período Analisado'
                    ],
                    'Valor': [
                        len(df_vendas),
                        int(df_vendas['Qtd. Matrículas'].sum()),
                        df_vendas['Nível'].nunique(),
                        df_vendas['Curso'].nunique(),
                        f"{ano if ano else 'Todos os anos'} - {mes if mes else 'Todos os meses'}"
                    ]
                }

                df_resumo = pd.DataFrame(resumo_data)
                df_resumo.to_excel(
                    writer, sheet_name='Resumo Geral', index=False)

                worksheet = writer.sheets['Resumo Geral']
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 20)
                worksheet.set_row(0, None, header_format)

                # Aba 2: Vendas por Modalidade
                modalidades_count = df_vendas.groupby(
                    'Nível')['Qtd. Matrículas'].sum().reset_index()
                modalidades_count = modalidades_count.sort_values(
                    'Qtd. Matrículas', ascending=False)
                modalidades_count.columns = [
                    'Modalidade', 'Total de Matrículas']
                modalidades_count.to_excel(
                    writer, sheet_name='Por Modalidade', index=False)

                worksheet = writer.sheets['Por Modalidade']
                worksheet.set_column('A:A', 30)
                worksheet.set_column('B:B', 20)
                worksheet.set_row(0, None, header_format)

                # Aba 3: Vendas por Curso
                cursos_count = df_vendas.groupby(
                    'Curso')['Qtd. Matrículas'].sum().reset_index()
                cursos_count = cursos_count.sort_values(
                    'Qtd. Matrículas', ascending=False)
                cursos_count.columns = ['Curso', 'Total de Matrículas']
                cursos_count.to_excel(
                    writer, sheet_name='Por Curso', index=False)

                worksheet = writer.sheets['Por Curso']
                worksheet.set_column('A:A', 40)
                worksheet.set_column('B:B', 20)
                worksheet.set_row(0, None, header_format)

                # Aba 4: Vendas por Mês (se ano especificado)
                if ano:
                    df_vendas['Mês'] = df_vendas['Dt Pagto'].dt.month
                    vendas_mensais = df_vendas.groupby(
                        'Mês')['Qtd. Matrículas'].sum().reset_index()

                    meses_nomes = {
                        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
                    }

                    vendas_mensais['Nome do Mês'] = vendas_mensais['Mês'].map(
                        meses_nomes)
                    vendas_mensais = vendas_mensais[[
                        'Nome do Mês', 'Qtd. Matrículas']]
                    vendas_mensais.columns = ['Mês', 'Total de Matrículas']
                    vendas_mensais.to_excel(
                        writer, sheet_name='Por Mês', index=False)

                    worksheet = writer.sheets['Por Mês']
                    worksheet.set_column('A:A', 15)
                    worksheet.set_column('B:B', 20)
                    worksheet.set_row(0, None, header_format)

            return output.getvalue()

        except Exception as e:
            st.error(f"Erro ao gerar relatório Excel: {str(e)}")
            return b""

    def generate_detailed_report_excel(self, parceiro_nome: str, ano: int = None, mes: int = None, modalidades: List[str] = None) -> bytes:
        """Gera relatório detalhado em Excel"""
        try:
            df_vendas = self.get_filtered_sales_data(
                parceiro_nome, ano, mes, modalidades)

            if df_vendas.empty:
                st.warning(
                    "Nenhum dado encontrado para os filtros selecionados.")
                return b""

            output = io.BytesIO()

            # Preparar dados para exportação
            df_export = df_vendas[['CPF', 'Aluno', 'Nível',
                                   'Curso', 'Dt Pagto', 'Qtd. Matrículas']].copy()
            df_export['Dt Pagto'] = df_export['Dt Pagto'].dt.strftime(
                '%d/%m/%Y')
            df_export = df_export.sort_values('Dt Pagto')

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book

                # Formatos
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#667eea',
                    'font_color': 'white',
                    'border': 1
                })

                # Aba principal com todos os dados
                df_export.to_excel(
                    writer, sheet_name='Dados Detalhados', index=False)

                worksheet = writer.sheets['Dados Detalhados']
                worksheet.set_column('A:A', 15)  # CPF
                worksheet.set_column('B:B', 30)  # Aluno
                worksheet.set_column('C:C', 20)  # Nível
                worksheet.set_column('D:D', 40)  # Curso
                worksheet.set_column('E:E', 12)  # Data
                worksheet.set_column('F:F', 15)  # Qtd
                worksheet.set_row(0, None, header_format)

                # Aba de resumo
                resumo_data = {
                    'Métrica': [
                        'Total de Registros',
                        'Total de Matrículas',
                        'Período',
                        'Modalidades Incluídas',
                        'Data de Geração'
                    ],
                    'Valor': [
                        len(df_export),
                        int(df_export['Qtd. Matrículas'].sum()),
                        f"{ano if ano else 'Todos os anos'} - {mes if mes else 'Todos os meses'}",
                        ', '.join(
                            modalidades) if modalidades and "Todas" not in modalidades else "Todas",
                        datetime.now().strftime('%d/%m/%Y %H:%M')
                    ]
                }

                df_resumo = pd.DataFrame(resumo_data)
                df_resumo.to_excel(writer, sheet_name='Resumo', index=False)

                worksheet = writer.sheets['Resumo']
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 30)
                worksheet.set_row(0, None, header_format)

            return output.getvalue()

        except Exception as e:
            st.error(f"Erro ao gerar relatório detalhado Excel: {str(e)}")
            return b""

    def generate_csv_report(self, parceiro_nome: str, ano: int = None, mes: int = None, modalidades: List[str] = None, detailed: bool = False) -> bytes:
        """Gera relatório em CSV"""
        try:
            df_vendas = self.get_filtered_sales_data(
                parceiro_nome, ano, mes, modalidades)

            if df_vendas.empty:
                return b""

            if detailed:
                # Relatório detalhado
                df_export = df_vendas[['CPF', 'Aluno', 'Nível',
                                       'Curso', 'Dt Pagto', 'Qtd. Matrículas']].copy()
                df_export['Dt Pagto'] = df_export['Dt Pagto'].dt.strftime(
                    '%d/%m/%Y')
            else:
                # Relatório resumido
                df_export = df_vendas.groupby(['Nível', 'Curso'])[
                    'Qtd. Matrículas'].sum().reset_index()
                df_export = df_export.sort_values(
                    'Qtd. Matrículas', ascending=False)

            output = io.StringIO()
            df_export.to_csv(output, index=False, encoding='utf-8-sig')
            return output.getvalue().encode('utf-8-sig')

        except Exception as e:
            st.error(f"Erro ao gerar CSV: {str(e)}")
            return b""

    def generate_pdf_report(self, parceiro_nome: str, ano: int = None, mes: int = None, modalidades: List[str] = None, detailed: bool = False) -> bytes:
        """Gera relatório em PDF"""
        try:
            df_vendas = self.get_filtered_sales_data(
                parceiro_nome, ano, mes, modalidades)

            if df_vendas.empty:
                return b""

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.HexColor('#667eea'),
                alignment=1  # Center
            )

            story.append(
                Paragraph(f"Relatório de Vendas - {parceiro_nome}", title_style))
            story.append(Spacer(1, 20))

            # Informações do relatório
            info_data = [
                ['Período:',
                    f"{ano if ano else 'Todos os anos'} - {mes if mes else 'Todos os meses'}"],
                ['Modalidades:', ', '.join(
                    modalidades) if modalidades and "Todas" not in modalidades else "Todas"],
                ['Data de Geração:', datetime.now().strftime('%d/%m/%Y %H:%M')],
                ['Total de Vendas:', str(len(df_vendas))],
                ['Total de Matrículas:', str(
                    int(df_vendas['Qtd. Matrículas'].sum()))]
            ]

            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(info_table)
            story.append(Spacer(1, 30))

            if detailed:
                # Tabela detalhada (limitada a primeiras 50 linhas)
                story.append(
                    Paragraph("Detalhamento das Vendas (Primeiras 50 linhas)", styles['Heading2']))
                story.append(Spacer(1, 10))

                df_limited = df_vendas.head(50)
                data = [['Aluno', 'Nível', 'Curso', 'Data', 'Qtd']]

                for _, row in df_limited.iterrows():
                    data.append([
                        row['Aluno'][:20] +
                        '...' if len(str(row['Aluno'])) > 20 else str(
                            row['Aluno']),
                        str(row['Nível']),
                        row['Curso'][:25] +
                        '...' if len(str(row['Curso'])) > 25 else str(
                            row['Curso']),
                        row['Dt Pagto'].strftime('%d/%m/%Y'),
                        str(int(row['Qtd. Matrículas']))
                    ])

                table = Table(data, colWidths=[
                              1.5*inch, 1*inch, 2*inch, 0.8*inch, 0.5*inch])

            else:
                # Tabela resumida por modalidade
                story.append(
                    Paragraph("Resumo por Modalidade", styles['Heading2']))
                story.append(Spacer(1, 10))

                modalidades_summary = df_vendas.groupby(
                    'Nível')['Qtd. Matrículas'].sum().reset_index()
                modalidades_summary = modalidades_summary.sort_values(
                    'Qtd. Matrículas', ascending=False)

                data = [['Modalidade', 'Total de Matrículas']]
                for _, row in modalidades_summary.iterrows():
                    data.append([str(row['Nível']), str(
                        int(row['Qtd. Matrículas']))])

                table = Table(data, colWidths=[3*inch, 2*inch])

            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)

            doc.build(story)
            return buffer.getvalue()

        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
            return b""
