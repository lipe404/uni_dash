# 🎓 UniDash – Dashboard Interativo de Vendas

Uma aplicação **dashboard interativo** desenvolvida em **Python** com **Streamlit**, integrada via **API ao Google Sheets**, para acompanhamento de vendas e relatórios de parceiros da UniÚnica.

## 🚀 Funcionalidades
- 🔐 **Login seguro** com autenticação de usuários parceiros.  
- 📊 **Dashboard individual** com indicadores personalizados por polo.  
- 📋 **Relatórios e metas** com exportação e visualização amigável.  
- 🌍 **Dashboard público** para visão geral consolidada.  
- 🎨 **Design customizado** com CSS e foco em acessibilidade, usabilidade e responsividade.  

## 🛠️ Tecnologias utilizadas
- **Python 3.11+**  
- [Streamlit](https://streamlit.io/) – construção da interface interativa  
- **Pandas, NumPy, Scikit-learn, Statsmodels** – manipulação e análise de dados  
- **Plotly & Altair** – visualizações gráficas  
- **Google Sheets API** – integração com bases de vendas e parceiros  
- **dotenv** – gerenciamento seguro de variáveis de ambiente  
- **OpenPyXL / XlsxWriter / PyArrow** – suporte a planilhas e exportações  

## 📂 Estrutura principal do projeto
📁 unidash/
├── app.py # Ponto de entrada principal
├── config.py # Configuração e integração com variáveis de ambiente
├── auth/ # Módulo de autenticação
├── app_sections/ # Seções do dashboard (individual, público, relatórios)
├── requirements.txt # Dependências do projeto
└── .env.example # Exemplo de variáveis de ambiente


## ⚙️ Instalação e execução local
```bash
# Clonar o repositório
git clone https://github.com/seuusuario/unidash.git
cd unidash

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (.env)
cp .env.example .env
# Adicione suas chaves da Google Sheets API no .env

# Rodar o projeto
streamlit run app.py
🔑 Variáveis de ambiente

O projeto usa variáveis sensíveis para conectar-se às planilhas. No arquivo .env você deve configurar:
GOOGLE_SHEETS_POLOS_API_KEY=xxxx
GOOGLE_SHEETS_POLOS_SHEET_ID=xxxx
GOOGLE_SHEETS_VENDAS_API_KEY=xxxx
GOOGLE_SHEETS_VENDAS_SHEET_ID=xxxx
GOOGLE_SHEETS_ALUNOS_API_KEY=xxxx
GOOGLE_SHEETS_ALUNOS_SHEET_ID=xxxx


👨‍💻 Autor
Desenvolvido por Felipe Toledo
