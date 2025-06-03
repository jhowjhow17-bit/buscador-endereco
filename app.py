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

        if len(datas_fo_

