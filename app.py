
import streamlit as st
import pandas as pd

# Título do app
st.set_page_config(page_title="Buscar Endereço", layout="centered")
st.title("🔍 Buscar Endereço")

# Carregando os dados
@st.cache_data
def carregar_dados():
    return pd.read_excel("ENDEREÇO CTOP FINAL Atualizado.xlsx")

df = carregar_dados()

# Opções de busca
coluna_busca = st.selectbox("Buscar por:", ["ID", "AT", "CIDADE"])

if coluna_busca == "CIDADE":
    cidade_escolhida = st.selectbox("Selecione a cidade:", sorted(df["CIDADE"].dropna().unique()))
    df_filtrado = df[df["CIDADE"] == cidade_escolhida]

    # Mostrar opções de AT dentro da cidade
    ats_disponiveis = df_filtrado["AT"].dropna().unique()
    at_escolhida = st.selectbox("Filtrar por AT:", ["Todas"] + sorted(ats_disponiveis.tolist()))
    if at_escolhida != "Todas":
        df_filtrado = df_filtrado[df_filtrado["AT"] == at_escolhida]

    # Filtro por FAC
    fac_unicas = df_filtrado["FAC"].dropna().unique()
    if len(fac_unicas) > 0:
        fac_escolhida = st.selectbox("Filtrar por FAC:", ["Todas"] + sorted(fac_unicas.tolist()))
        if fac_escolhida != "Todas":
            df_filtrado = df_filtrado[df_filtrado["FAC"] == fac_escolhida]

elif coluna_busca in ["ID", "AT"]:
    valor_busca = st.text_input(f"Digite o valor de {coluna_busca}:")

    if valor_busca:
        df_filtrado = df[df[coluna_busca].astype(str).str.contains(valor_busca, case=False, na=False)]

        # Filtro por FAC
        fac_unicas = df_filtrado["FAC"].dropna().unique()
        if len(fac_unicas) > 0:
            fac_escolhida = st.selectbox("Filtrar por FAC:", ["Todas"] + sorted(fac_unicas.tolist()))
            if fac_escolhida != "Todas":
                df_filtrado = df_filtrado[df_filtrado["FAC"] == fac_escolhida]
else:
    df_filtrado = pd.DataFrame()

# Exibir resultados
if not df_filtrado.empty:
    st.markdown(f"### Resultados encontrados: {len(df_filtrado)}")
    st.dataframe(df_filtrado[["ID", "AT", "Endereço", "CIDADE", "CTO", "FAC"]].reset_index(drop=True))
elif coluna_busca in ["ID", "AT"] and not valor_busca:
    st.info("Digite um valor para iniciar a busca.")
