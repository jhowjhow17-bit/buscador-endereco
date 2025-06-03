import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Configuração da página
st.set_page_config(page_title="Buscar Endereço", layout="centered")

USERS_FILE = "usuarios.json"

# Cria arquivo de usuários caso não exista
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({"Jonathan": "Jacare@92", "admin": "1234"}, f)

# Carrega usuários
with open(USERS_FILE, "r") as f:
    usuarios_autorizados = json.load(f)

def salvar_usuarios(usuarios):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios, f)

def registrar_acesso(usuario):
    with open("log_acessos.txt", "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {usuario}\n")

def exibir_log():
    try:
        with open("log_acessos.txt", "r") as f:
            log_linhas = f.readlines()

        datas = [linha.split(" - ")[0] for linha in log_linhas]
        datas_formatadas = [datetime.strptime(data, "%Y-%m-%d %H:%M:%S").date() for data in datas]

        if len(datas_formatadas) == 0:
            st.warning("Nenhum registro no log para mostrar.")
            return

        data_inicio = st.date_input("📅 Data inicial:", min(datas_formatadas))
        data_fim = st.date_input("📅 Data final:", max(datas_formatadas))

        log_filtrado = ""
        for linha, data in zip(log_linhas, datas_formatadas):
            if data_inicio <= data <= data_fim:
                log_filtrado += linha

        st.text_area("📋 Log de Acessos:", log_filtrado, height=200)
    except FileNotFoundError:
        st.warning("Arquivo de log ainda não existe.")

# Controle de sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.usuario = ""

if "expander_open" not in st.session_state:
    st.session_state.expander_open = False

def abrir_expander():
    st.session_state.expander_open = True

def logout():
    st.session_state.logged_in = False
    st.session_state.usuario = ""
    st.experimental_rerun()

# Tela de login
if not st.session_state.logged_in:
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in usuarios_autorizados and usuarios_autorizados[usuario] == senha:
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            registrar_acesso(usuario)
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos.")
else:
    # Usuário logado
    st.sidebar.button("Logout", on_click=logout)
    st.success(f"Bem-vindo, {st.session_state.usuario}!")

    usuario = st.session_state.usuario

    # Mostrar log para admin e Jonathan
    if usuario in ["admin", "Jonathan"]:
        if st.checkbox("👁️ Ver log de acessos"):
            exibir_log()

    # Cadastro de novos usuários para admin e Jonathan
    if usuario in ["admin", "Jonathan"]:
        with st.expander("➕ Cadastrar novo usuário", expanded=st.session_state.expander_open):
            with st.form("form_cadastro_usuario"):
                novo_user = st.text_input("Novo usuário", on_change=abrir_expander)
                nova_senha = st.text_input("Senha do novo usuário", type="password", on_change=abrir_expander)
                enviar = st.form_submit_button("Criar usuário")
                if enviar:
                    if novo_user in usuarios_autorizados:
                        st.warning("Usuário já existe.")
                    elif novo_user.strip() == "" or nova_senha.strip() == "":
                        st.warning("Preencha os campos para novo usuário e senha.")
                    else:
                        usuarios_autorizados[novo_user] = nova_senha
                        salvar_usuarios(usuarios_autorizados)
                        st.success(f"Usuário '{novo_user}' criado com sucesso!")
                        st.session_state.expander_open = False

    # Busca de endereço
    st.title("🔍 Buscar Endereço")

    @st.cache_data
    def carregar_dados():
        return pd.read_excel("ENDEREÇO CTOP FINAL Atualizado.xlsx")

    df = carregar_dados()

    cidade_escolhida = st.selectbox("1️⃣ Selecione a Cidade:", sorted(df["CIDADE"].dropna().unique()))
    df_filtrado = df[df["CIDADE"] == cidade_escolhida]

    ats_disponiveis = df_filtrado["AT"].dropna().unique()
    at_escolhida = st.selectbox("2️⃣ Filtrar por AT:", ["Todas"] + sorted(ats_disponiveis.tolist()))
    if at_escolhida != "Todas":
        df_filtrado = df_filtrado[df_filtrado["AT"] == at_escolhida]

    fac_unicas = df_filtrado["FAC"].dropna().unique()
    if len(fac_unicas) > 0:
        fac_escolhida = st.selectbox("3️⃣ Filtrar por FAC:", ["Todas"] + sorted(fac_unicas.tolist()))
        if fac_escolhida != "Todas":
            df_filtrado = df_filtrado[df_filtrado["FAC"] == fac_escolhida]

    if not df_filtrado.empty:
        st.markdown(f"### Resultados encontrados: {len(df_filtrado)}")
        st.dataframe(df_filtrado[["ID", "AT", "Endereço", "CIDADE", "CTO", "FAC"]].reset_index(drop=True))
    else:
        st.info("Nenhum resultado encontrado para os filtros selecionados.")
