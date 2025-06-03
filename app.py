import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Título do app
st.set_page_config(page_title="Buscar Endereço", layout="centered")

# --- Gerenciamento de Usuários ---
USERS_FILE = "usuarios.json"

# Carregar ou criar usuários autorizados
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({"Jonathan": "Jacare@92", "admin": "1234"}, f)

with open(USERS_FILE, "r") as f:
    usuarios_autorizados = json.load(f)

def salvar_usuarios(usuarios):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios, f)

# Função para registrar acessos
def registrar_acesso(usuario):
    with open("log_acessos.txt", "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {usuario}\n")

# Função para exibir log de acessos com filtro de data
def exibir_log():
    try:
        with open("log_acessos.txt", "r") as f:
            log_linhas = f.readlines()

        datas = [linha.split(" - ")[0] for linha in log_linhas]
        datas_formatadas = [datetime.strptime(data, "%Y-%m-%d %H:%M:%S").date() for data in datas]

        data_inicio = st.date_input("📅 Data inicial:", min(datas_formatadas))
        data_fim = st.date_input("📅 Data final:", max(datas_formatadas))

        log_filtrado = ""
        for linha, data in zip(log_linhas, datas_formatadas):
            if data_inicio <= data <= data_fim:
                log_filtrado += linha

        st.text_area("📋 Log de Acessos:", log_filtrado, height=200)
    except FileNotFoundError:
        st.warning("Arquivo de log ainda não existe.")

# Login
st.title("🔐 Login")
usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if usuario in usuarios_autorizados and usuarios_autorizados[usuario] == senha:
        registrar_acesso(usuario)
        st.success("Login realizado com sucesso!")

        # Mostrar log e gerenciar usuários apenas para admin ou Jonathan
        if usuario in ["admin", "Jonathan"]:
            if st.checkbox("👁️ Ver log de acessos"):
                exibir_log()

            if st.checkbox("➕ Cadastrar novo usuário"):
                novo_user = st.text_input("Novo usuário")
                nova_senha = st.text_input("Senha do novo usuário", type="password")
                if st.button("Criar usuário"):
                    if novo_user in usuarios_autorizados:
                        st.warning("Usuário já existe.")
                    else:
                        usuarios_autorizados[novo_user] = nova_senha
                        salvar_usuarios(usuarios_autorizados)
                        st.success(f"Usuário '{novo_user}' criado com sucesso!")

        st.title("🔍 Buscar Endereço")

        # Carregando os dados
        @st.cache_data
        def carregar_dados():
            return pd.read_excel("ENDEREÇO CTOP FINAL Atualizado.xlsx")

        df = carregar_dados()

        # Menu de cidade como primeira etapa obrigatória
        cidade_escolhida = st.selectbox("1️⃣ Selecione a Cidade:", sorted(df["CIDADE"].dropna().unique()))
        df_filtrado = df[df["CIDADE"] == cidade_escolhida]

        # Filtro por AT dentro da cidade
        ats_disponiveis = df_filtrado["AT"].dropna().unique()
        at_escolhida = st.selectbox("2️⃣ Filtrar por AT:", ["Todas"] + sorted(ats_disponiveis.tolist()))
        if at_escolhida != "Todas":
            df_filtrado = df_filtrado[df_filtrado["AT"] == at_escolhida]

        # Filtro por FAC
        fac_unicas = df_filtrado["FAC"].dropna().unique()
        if len(fac_unicas) > 0:
            fac_escolhida = st.selectbox("3️⃣ Filtrar por FAC:", ["Todas"] + sorted(fac_unicas.tolist()))
            if fac_escolhida != "Todas":
                df_filtrado = df_filtrado[df_filtrado["FAC"] == fac_escolhida]

        # Exibir resultados
        if not df_filtrado.empty:
            st.markdown(f"### Resultados encontrados: {len(df_filtrado)}")
            st.dataframe(df_filtrado[["ID", "AT", "Endereço", "CIDADE", "CTO", "FAC"]].reset_index(drop=True))
        else:
            st.info("Nenhum resultado encontrado para os filtros selecionados.")
    else:
        st.error("Usuário ou senha inválidos.")
