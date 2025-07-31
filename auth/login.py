import streamlit as st
import pandas as pd
from data.fetch_data import fetch_parceiros_data
from typing import Optional, Dict, Any


class AuthManager:
    def __init__(self):
        self.session_key = "authenticated_user"

    def authenticate_user(self, user_id: str, chave: str) -> Optional[Dict[str, Any]]:
        """
        Autentica o usuário com base no ID e CHAVE da planilha
        """
        try:
            # Busca dados dos parceiros
            df_parceiros = fetch_parceiros_data()

            if df_parceiros is not None and not df_parceiros.empty:
                # Filtra pelo ID e CHAVE
                user_data = df_parceiros[
                    (df_parceiros['ID'].astype(str) == str(user_id)) &
                    (df_parceiros['CHAVE'].astype(str) == str(chave))
                ]

                if not user_data.empty:
                    user_info = user_data.iloc[0]
                    return {
                        'parceiro': user_info['Parceiro - VENDAS PINCEL + GESTOR'],
                        'tipo': user_info['TIPO'],
                        'responsavel': user_info['RESPONSÁVEL'],
                        'id': user_info['ID'],
                        'authenticated': True
                    }

            return None

        except Exception as e:
            st.error(f"Erro na autenticação: {str(e)}")
            return None

    def login_form(self):
        """
        Renderiza o formulário de login
        """
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>UniUnica Dashboard</h1>
            <h3>Sistema de Acompanhamento Individual de Vendas</h3>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### 🔐 Acesso ao Sistema")

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                user_id = st.text_input(
                    "🆔 ID de Acesso", placeholder="Digite seu ID")
                chave = st.text_input(
                    "🔑 Chave de Acesso", type="password", placeholder="Digite sua chave")

                submitted = st.form_submit_button(
                    "🚀 Entrar", use_container_width=True)

                if submitted:
                    if user_id and chave:
                        user_data = self.authenticate_user(user_id, chave)

                        if user_data:
                            st.session_state[self.session_key] = user_data
                            st.success(
                                f"✅ Bem-vindo(a), {user_data['parceiro']}!")
                            st.rerun()
                        else:
                            st.error(
                                "❌ ID ou Chave incorretos. Tente novamente.")
                    else:
                        st.warning("⚠️ Por favor, preencha todos os campos.")

    def is_authenticated(self) -> bool:
        """
        Verifica se o usuário está autenticado
        """
        return self.session_key in st.session_state and st.session_state[self.session_key].get('authenticated', False)

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Retorna os dados do usuário atual
        """
        if self.is_authenticated():
            return st.session_state[self.session_key]
        return None

    def logout(self):
        """
        Realiza o logout do usuário
        """
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]
        st.rerun()

    def render_logout_button(self):
        """
        Renderiza o botão de logout no sidebar
        """
        user = self.get_current_user()
        if user:
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"**👤 Usuário:** {user['parceiro']}")
            st.sidebar.markdown(f"**🏢 Tipo:** {user['tipo']}")

            if st.sidebar.button("🚪 Sair", use_container_width=True):
                self.logout()
