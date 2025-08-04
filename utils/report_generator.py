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

                currency_format = workbook.add_format(
                    {'num_format': 'R\$ #,##0.00'})
                number_format = workbook.add_format({'num_format': '#,##0'})

                # Aba 1: Resumo Geral
                # Calcular valor total se a coluna existir
                valor_total = 0
                if 'Valor Taxa Matrícula' in df_vendas.columns:
                    # Converter para numérico, tratando valores não numéricos
                    df_vendas['Valor Taxa Matrícula'] = pd.to_numeric(
                        df_vendas['Valor Taxa Matrícula'].astype(str).str.replace(
                            'R\$', '').str.replace(',', '.').str.strip(),
                        errors='coerce'
                    ).fillna(0)
                    valor_total = df_vendas['Valor Taxa Matrícula'].sum()

                resumo_data = {
                    'Métrica': [
                        'Total de Vendas',
                        'Total de Matrículas',
                        'Valor Total Arrecadado',
                        'Modalidades Diferentes',
                        'Cursos Diferentes',
                        'IES Diferentes',
                        'Período Analisado'
                    ],
                    'Valor': [
                        len(df_vendas),
                        int(df_vendas['Qtd. Matrículas'].sum()),
                        f"R\$ {valor_total:,.2f}".replace(
                            ',', 'X').replace('.', ',').replace('X', '.'),
                        df_vendas['Nível'].nunique(),
                        df_vendas['Curso'].nunique(),
                        df_vendas['IES'].nunique(
                        ) if 'IES' in df_vendas.columns else 0,
                        f"{ano if ano else 'Todos os anos'} - {mes if mes else 'Todos os meses'}"
                    ]
                }

                df_resumo = pd.DataFrame(resumo_data)
                df_resumo.to_excel(
                    writer, sheet_name='Resumo Geral', index=False)

                worksheet = writer.sheets['Resumo Geral']
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 25)
                worksheet.set_row(0, None, header_format)

                # Aba 2: Vendas por Modalidade
                modalidades_count = df_vendas.groupby('Nível').agg({
                    'Qtd. Matrículas': 'sum',
                    'Valor Taxa Matrícula': 'sum' if 'Valor Taxa Matrícula' in df_vendas.columns else lambda x: 0
                }).reset_index()
                modalidades_count = modalidades_count.sort_values(
                    'Qtd. Matrículas', ascending=False)
                modalidades_count.columns = [
                    'Modalidade', 'Total de Matrículas', 'Valor Total']

                # Formatar valores monetários
                if 'Valor Total' in modalidades_count.columns:
                    modalidades_count['Valor Total'] = modalidades_count['Valor Total'].apply(
                        lambda x: f"R\$ {x:,.2f}".replace(
                            ',', 'X').replace('.', ',').replace('X', '.')
                    )

                modalidades_count.to_excel(
                    writer, sheet_name='Por Modalidade', index=False)

                worksheet = writer.sheets['Por Modalidade']
                worksheet.set_column('A:A', 30)
                worksheet.set_column('B:B', 20)
                worksheet.set_column('C:C', 20)
                worksheet.set_row(0, None, header_format)

                # Aba 3: Vendas por Curso
                cursos_count = df_vendas.groupby('Curso').agg({
                    'Qtd. Matrículas': 'sum',
                    'Valor Taxa Matrícula': 'sum' if 'Valor Taxa Matrícula' in df_vendas.columns else lambda x: 0
                }).reset_index()
                cursos_count = cursos_count.sort_values(
                    'Qtd. Matrículas', ascending=False)
                cursos_count.columns = [
                    'Curso', 'Total de Matrículas', 'Valor Total']

                # Formatar valores monetários
                if 'Valor Total' in cursos_count.columns:
                    cursos_count['Valor Total'] = cursos_count['Valor Total'].apply(
                        lambda x: f"R\$ {x:,.2f}".replace(
                            ',', 'X').replace('.', ',').replace('X', '.')
                    )

                cursos_count.to_excel(
                    writer, sheet_name='Por Curso', index=False)

                worksheet = writer.sheets['Por Curso']
                worksheet.set_column('A:A', 40)
                worksheet.set_column('B:B', 20)
                worksheet.set_column('C:C', 20)
                worksheet.set_row(0, None, header_format)

                # Aba 4: Vendas por IES (se a coluna existir)
                if 'IES' in df_vendas.columns:
                    ies_count = df_vendas.groupby('IES').agg({
                        'Qtd. Matrículas': 'sum',
                        'Valor Taxa Matrícula': 'sum' if 'Valor Taxa Matrícula' in df_vendas.columns else lambda x: 0
                    }).reset_index()
                    ies_count = ies_count.sort_values(
                        'Qtd. Matrículas', ascending=False)
                    ies_count.columns = [
                        'IES', 'Total de Matrículas', 'Valor Total']

                    # Formatar valores monetários
                    if 'Valor Total' in ies_count.columns:
                        ies_count['Valor Total'] = ies_count['Valor Total'].apply(
                            lambda x: f"R\$ {x:,.2f}".replace(
                                ',', 'X').replace('.', ',').replace('X', '.')
                        )

                    ies_count.to_excel(
                        writer, sheet_name='Por IES', index=False)

                    worksheet = writer.sheets['Por IES']
                    worksheet.set_column('A:A', 40)
                    worksheet.set_column('B:B', 20)
                    worksheet.set_column('C:C', 20)
                    worksheet.set_row(0, None, header_format)

                # Aba 5: Vendas por Mês (se ano especificado)
                if ano:
                    df_vendas['Mês'] = df_vendas['Dt Pagto'].dt.month
                    vendas_mensais = df_vendas.groupby('Mês').agg({
                        'Qtd. Matrículas': 'sum',
                        'Valor Taxa Matrícula': 'sum' if 'Valor Taxa Matrícula' in df_vendas.columns else lambda x: 0
                    }).reset_index()

                    meses_nomes = {
                        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
                    }

                    vendas_mensais['Nome do Mês'] = vendas_mensais['Mês'].map(
                        meses_nomes)
                    vendas_mensais = vendas_mensais[[
                        'Nome do Mês', 'Qtd. Matrículas', 'Valor Taxa Matrícula']]
                    vendas_mensais.columns = [
                        'Mês', 'Total de Matrículas', 'Valor Total']

                    # Formatar valores monetários
                    if 'Valor Total' in vendas_mensais.columns:
                        vendas_mensais['Valor Total'] = vendas_mensais['Valor Total'].apply(
                            lambda x: f"R\$ {x:,.2f}".replace(
                                ',', 'X').replace('.', ',').replace('X', '.')
                        )

                    vendas_mensais.to_excel(
                        writer, sheet_name='Por Mês', index=False)

                    worksheet = writer.sheets['Por Mês']
                    worksheet.set_column('A:A', 15)
                    worksheet.set_column('B:B', 20)
                    worksheet.set_column('C:C', 20)
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

            # Preparar dados para exportação com as novas colunas
            colunas_export = ['Parceiro', 'Aluno', 'Nível', 'Curso',
                              'IES', 'Dt Pagto', 'Qtd. Matrículas', 'Valor Taxa Matrícula']

            # Verificar quais colunas existem no DataFrame
            colunas_disponiveis = [
                col for col in colunas_export if col in df_vendas.columns]

            df_export = df_vendas[colunas_disponiveis].copy()
            df_export['Dt Pagto'] = df_export['Dt Pagto'].dt.strftime(
                '%d/%m/%Y')
            df_export = df_export.sort_values('Dt Pagto')

            # Tratar valores monetários
            if 'Valor Taxa Matrícula' in df_export.columns:
                df_export['Valor Taxa Matrícula'] = pd.to_numeric(
                    df_export['Valor Taxa Matrícula'].astype(str).str.replace(
                        'R\$', '').str.replace(',', '.').str.strip(),
                    errors='coerce'
                ).fillna(0)
                # Formatar como moeda brasileira
                df_export['Valor Taxa Matrícula'] = df_export['Valor Taxa Matrícula'].apply(
                    lambda x: f"R\$ {x:,.2f}".replace(
                        ',', 'X').replace('.', ',').replace('X', '.')
                )

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
                worksheet.set_column('A:A', 25)  # Parceiro
                worksheet.set_column('B:B', 30)  # Aluno
                worksheet.set_column('C:C', 20)  # Nível
                worksheet.set_column('D:D', 40)  # Curso
                worksheet.set_column('E:E', 25)  # IES
                worksheet.set_column('F:F', 12)  # Data
                worksheet.set_column('G:G', 15)  # Qtd
                worksheet.set_column('H:H', 18)  # Valor
                worksheet.set_row(0, None, header_format)

                # Aba de resumo
                valor_total = 0
                if 'Valor Taxa Matrícula' in df_vendas.columns:
                    valor_numerico = pd.to_numeric(
                        df_vendas['Valor Taxa Matrícula'].astype(str).str.replace(
                            'R\$', '').str.replace(',', '.').str.strip(),
                        errors='coerce'
                    ).fillna(0)
                    valor_total = valor_numerico.sum()

                resumo_data = {
                    'Métrica': [
                        'Total de Registros',
                        'Total de Matrículas',
                        'Valor Total Arrecadado',
                        'Período',
                        'Modalidades Incluídas',
                        'Data de Geração'
                    ],
                    'Valor': [
                        len(df_export),
                        int(df_export['Qtd. Matrículas'].sum(
                        )) if 'Qtd. Matrículas' in df_export.columns else 0,
                        f"R\$ {valor_total:,.2f}".replace(
                            ',', 'X').replace('.', ',').replace('X', '.'),
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
                # Relatório detalhado com as novas colunas
                colunas_export = ['Parceiro', 'Aluno', 'Nível', 'Curso',
                                  'IES', 'Dt Pagto', 'Qtd. Matrículas', 'Valor Taxa Matrícula']
                colunas_disponiveis = [
                    col for col in colunas_export if col in df_vendas.columns]

                df_export = df_vendas[colunas_disponiveis].copy()
                df_export['Dt Pagto'] = df_export['Dt Pagto'].dt.strftime(
                    '%d/%m/%Y')

                # Tratar valores monetários
                if 'Valor Taxa Matrícula' in df_export.columns:
                    df_export['Valor Taxa Matrícula'] = pd.to_numeric(
                        df_export['Valor Taxa Matrícula'].astype(str).str.replace(
                            'R\$', '').str.replace(',', '.').str.strip(),
                        errors='coerce'
                    ).fillna(0)
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

            # Calcular valor total
            valor_total = 0
            if 'Valor Taxa Matrícula' in df_vendas.columns:
                valor_numerico = pd.to_numeric(
                    df_vendas['Valor Taxa Matrícula'].astype(str).str.replace(
                        'R\$', '').str.replace(',', '.').str.strip(),
                    errors='coerce'
                ).fillna(0)
                valor_total = valor_numerico.sum()

            # Informações do relatório
            info_data = [
                ['Período:',
                    f"{ano if ano else 'Todos os anos'} - {mes if mes else 'Todos os meses'}"],
                ['Modalidades:', ', '.join(
                    modalidades) if modalidades and "Todas" not in modalidades else "Todas"],
                ['Data de Geração:', datetime.now().strftime('%d/%m/%Y %H:%M')],
                ['Total de Vendas:', str(len(df_vendas))],
                ['Total de Matrículas:', str(
                    int(df_vendas['Qtd. Matrículas'].sum()))],
                ['Valor Total:', f"R\$ {valor_total:,.2f}".replace(
                    ',', 'X').replace('.', ',').replace('X', '.')]
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
                # Tabela detalhada (limitada a primeiras 30 linhas)
                story.append(
                    Paragraph("Detalhamento das Vendas (Primeiras 30 linhas)", styles['Heading2']))
                story.append(Spacer(1, 10))

                df_limited = df_vendas.head(30)
                data = [['Aluno', 'Nível', 'Curso', 'IES', 'Data']]

                for _, row in df_limited.iterrows():
                    data.append([
                        row['Aluno'][:15] +
                        '...' if len(str(row['Aluno'])) > 15 else str(
                            row['Aluno']),
                        str(row['Nível'])[
                            :15] + '...' if len(str(row['Nível'])) > 15 else str(row['Nível']),
                        row['Curso'][:20] +
                        '...' if len(str(row['Curso'])) > 20 else str(
                            row['Curso']),
                        row['IES'][:15] + '...' if 'IES' in row and len(
                            str(row['IES'])) > 15 else str(row.get('IES', 'N/A')),
                        row['Dt Pagto'].strftime('%d/%m/%Y')
                    ])

                table = Table(data, colWidths=[
                              1.2*inch, 1*inch, 1.5*inch, 1*inch, 0.8*inch])

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
