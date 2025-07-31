import streamlit as st
from auth.login import AuthManager
from app_sections.dashboard_individual import render_dashboard_individual
from app_sections.dashboard_publico import render_dashboard_publico

# Configuração da página
st.set_page_config(
    page_title="UniUnica Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }

    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Inicializar gerenciador de autenticação
    auth_manager = AuthManager()

    # Verificar se o usuário está autenticado
    if not auth_manager.is_authenticated():
        # Mostrar tela de login
        auth_manager.login_form()
    else:
        # Usuário autenticado - mostrar dashboard
        user = auth_manager.get_current_user()

        # Sidebar com navegação
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>UniUnica</h2>
            <p>Sua dashboard individual de acompanhamento de vendas</p>
        </div>
        """, unsafe_allow_html=True)

        # Menu de navegação
        menu_options = ["📊 Meu Dashboard", "🌍 Dashboard Público"]
        selected_page = st.sidebar.selectbox("📋 Navegação", menu_options)

        # Botão de logout
        auth_manager.render_logout_button()

        # Renderizar página selecionada
        if selected_page == "📊 Meu Dashboard":
            render_dashboard_individual(user['parceiro'])
        elif selected_page == "🌍 Dashboard Público":
            render_dashboard_publico()


if __name__ == "__main__":
    main()
