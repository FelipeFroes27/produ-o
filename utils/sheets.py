import unicodedata
from datetime import datetime, timedelta, timezone

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "10_J6pYgEcQNNQjwWIZCaeNPeOo928GoQ3zENwpLtWSc"
ABAS_PLANEJAMENTO = ["Produ\u00e7\u00e3o", "Manuten\u00e7\u00e3o", "Pe\u00e7as"]
ABA_USUARIOS = "Usu\u00e1rios"
ABA_HISTORICO = "Hist\u00f3rico"
FUSO_BRASILIA = timezone(timedelta(hours=-3))
COLUNAS_USUARIOS = ["Codigo", "Nome"]
COLUNAS_ORDENS = [
    "USUARIO_RESPONSAVEL",
    "STATUS",
    "OP",
    "COD_PRODUTO",
    "PRODUTO",
    "COD_PECA",
    "PECA",
    "QTD_PECAS",
    "QUANTIDADE",
    "REALIZADO",
    "DATA_ABERTURA",
    "DATA_PREVISTA",
    "DATA",
    "OBS",
    "ABA_ORIGEM",
    "LINHA_PLANILHA",
    "PECAS_BLOCO",
    "QUANTIDADE_NUM",
    "REALIZADO_NUM",
    "SALDO_NUM",
    "DATA_PRIORIDADE",
    "DIAS_ATRASO",
    "ATRASADA",
]
COLUNAS_HISTORICO = [
    "USUARIO_RESPONSAVEL",
    "OP",
    "DATA_HORA",
    "DATA_HORA_DT",
    "DATA",
    "CODIGO",
    "PRODUTO",
    "QUANTIDADE",
    "QUANTIDADE_NUM",
    "TIPO",
    "ACAO",
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def conectar():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


@st.cache_resource
def abrir_planilha():
    return conectar().open_by_key(SPREADSHEET_ID)


@st.cache_data(ttl=180)
def carregar_usuarios():
    worksheet = abrir_planilha().worksheet(ABA_USUARIOS)
    df = pd.DataFrame(worksheet.get_all_records(numericise_ignore=["all"]))
    df = _limpar_dataframe(df)
    df = _garantir_colunas(df, COLUNAS_USUARIOS)

    if "Codigo" in df.columns:
        df = df[df["Codigo"].astype(str).str.strip() != ""]
    if "Nome" in df.columns:
        df = df[df["Nome"].astype(str).str.strip() != ""]

    return df


@st.cache_data(ttl=180)
def carregar_ordens():
    frames = []

    for nome_aba in ABAS_PLANEJAMENTO:
        worksheet = abrir_planilha().worksheet(nome_aba)
        values = worksheet.get_all_values()
        if not values:
            continue

        headers = [str(coluna).strip() for coluna in values[0]]
        rows = []
        for row_index, row in enumerate(values[1:], start=2):
            registro = {
                header: str(row[pos]).strip() if pos < len(row) else ""
                for pos, header in enumerate(headers)
                if header
            }
            registro["ABA_ORIGEM"] = nome_aba
            registro["LINHA_PLANILHA"] = row_index
            rows.append(registro)

        df = pd.DataFrame(rows)
        df = _limpar_dataframe(df)
        df = _remover_linhas_de_cabecalho_repetido(df)
        if nome_aba == "Pe\u00e7as":
            df = _vincular_pecas_a_ordem(df)
        frames.append(df)

    if not frames:
        return _ordens_vazias()

    ordens = pd.concat(frames, ignore_index=True, sort=False)
    return _padronizar_ordens(ordens)


def carregar_resumo():
    return carregar_usuarios(), carregar_ordens()


@st.cache_data(ttl=180)
def carregar_historico():
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    values = worksheet.get_all_values()
    if not values:
        return _historico_vazio()

    headers = [str(coluna).strip() for coluna in values[0]]
    rows = []
    for row in values[1:]:
        registro = {
            header: str(row[pos]).strip() if pos < len(row) else ""
            for pos, header in enumerate(headers)
            if header
        }
        rows.append(registro)

    df = pd.DataFrame(rows)
    df = _limpar_dataframe(df)
    if df.empty:
        return _historico_vazio()

    colunas = {
        "USUARIO_RESPONSAVEL": _encontrar_coluna(df, ["USUÁRIO RESPONSAVEL", "USUARIO RESPONSAVEL"]),
        "OP": _encontrar_coluna(df, ["N° DA OP", "N DA OP", "OP"]),
        "DATA_HORA": _encontrar_coluna(df, ["DATA / HORA", "DATA HORA"]),
        "CODIGO": _encontrar_coluna(df, ["CODIGO"]),
        "PRODUTO": _encontrar_coluna(df, ["PRODUTO"]),
        "QUANTIDADE": _encontrar_coluna(df, ["QUANTIDADE"]),
        "TIPO": _encontrar_coluna(df, ["TIPO"]),
        "ACAO": _encontrar_coluna(df, ["A\u00c7\u00c3O", "ACAO"]),
    }

    for nome_padrao, coluna_origem in colunas.items():
        if coluna_origem is None:
            df[nome_padrao] = ""
        else:
            df[nome_padrao] = df[coluna_origem].astype(str).str.strip()

    campos_chave = ["USUARIO_RESPONSAVEL", "OP", "CODIGO", "PRODUTO", "QUANTIDADE", "TIPO"]
    tem_dados = df[campos_chave].apply(lambda linha: any(str(valor).strip() for valor in linha), axis=1)
    df = df[tem_dados].copy()
    df["QUANTIDADE_NUM"] = _serie_numero(df["QUANTIDADE"])
    df["DATA_HORA_DT"] = pd.to_datetime(df["DATA_HORA"], dayfirst=True, errors="coerce")
    df["DATA"] = df["DATA_HORA_DT"].dt.normalize()

    return _garantir_colunas(df, COLUNAS_HISTORICO)


def lancar_realizacao(ordem, quantidade_lancada):
    aba_origem = str(ordem["ABA_ORIGEM"])
    linha_planilha = int(ordem["LINHA_PLANILHA"])
    quantidade_lancada = float(quantidade_lancada)

    if quantidade_lancada <= 0:
        raise ValueError("Informe uma quantidade maior que zero.")

    worksheet = abrir_planilha().worksheet(aba_origem)
    headers = worksheet.row_values(1)
    coluna_realizado = _indice_coluna(headers, "REALIZADO")
    realizado_atual = _numero_celula(worksheet.cell(linha_planilha, coluna_realizado).value)
    saldo = max(float(ordem["QUANTIDADE_NUM"]) - realizado_atual, 0)

    if quantidade_lancada > saldo:
        raise ValueError(f"A quantidade lancada passa do saldo pendente ({_formatar_numero(saldo)}).")

    novo_realizado = realizado_atual + quantidade_lancada

    worksheet.update_cell(linha_planilha, coluna_realizado, _formatar_numero(novo_realizado))
    registrar_historico(ordem, quantidade_lancada, "Fim")

    carregar_ordens.clear()


def lancar_inicio_ordem(ordem):
    registrar_historico(ordem, 0, "Inicio")
    carregar_historico.clear()


def registrar_historico(ordem, quantidade_lancada, acao):
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    headers = worksheet.row_values(1)
    data_hora = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M:%S")
    linha = []

    for header in headers:
        header_normalizado = _normalizar(header)
        if header_normalizado == _normalizar("USU\u00c1RIO RESPONSAVEL"):
            linha.append(str(ordem.get("USUARIO_RESPONSAVEL", "")))
        elif header_normalizado == _normalizar("N\u00b0 DA OP"):
            linha.append(str(ordem.get("OP", "")))
        elif header_normalizado == _normalizar("DATA / HORA"):
            linha.append(data_hora)
        elif header_normalizado == "CODIGO":
            linha.append(str(ordem.get("COD_PRODUTO", "")))
        elif header_normalizado == "PRODUTO":
            linha.append(str(ordem.get("PRODUTO", "")))
        elif header_normalizado == "QUANTIDADE":
            linha.append(_formatar_numero(quantidade_lancada))
        elif header_normalizado == "TIPO":
            linha.append(str(ordem.get("ABA_ORIGEM", "")))
        elif header_normalizado == "ACAO":
            linha.append(str(acao))
        else:
            linha.append("")

    worksheet.append_row(linha, value_input_option="RAW")
    carregar_historico.clear()


def _limpar_dataframe(df):
    df = df.copy()
    df.columns = [str(coluna).strip() for coluna in df.columns]
    df = df.dropna(how="all")
    df = df.loc[:, [coluna for coluna in df.columns if str(coluna).strip()]]

    for coluna in df.columns:
        df[coluna] = df[coluna].fillna("").astype(str).str.strip()

    return df


def _garantir_colunas(df, colunas):
    df = df.copy()
    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = pd.Series(dtype=_dtype_coluna(coluna))
    return df


def _dtype_coluna(coluna):
    if coluna in ["QUANTIDADE_NUM", "REALIZADO_NUM", "SALDO_NUM", "DIAS_ATRASO"]:
        return "float64"
    if coluna in ["DATA_PRIORIDADE", "DATA_HORA_DT", "DATA"]:
        return "datetime64[ns]"
    if coluna == "ATRASADA":
        return "bool"
    return "object"


def _ordens_vazias():
    return pd.DataFrame({
        coluna: pd.Series(dtype=_dtype_coluna(coluna))
        for coluna in COLUNAS_ORDENS
    })


def _historico_vazio():
    return pd.DataFrame({
        coluna: pd.Series(dtype=_dtype_coluna(coluna))
        for coluna in COLUNAS_HISTORICO
    })


def _remover_linhas_de_cabecalho_repetido(df):
    if df.empty:
        return df

    primeira_coluna = next(
        (coluna for coluna in df.columns if coluna not in ["ABA_ORIGEM", "LINHA_PLANILHA"]),
        df.columns[0],
    )
    return df[df[primeira_coluna].astype(str).str.strip() != primeira_coluna].copy()


def _padronizar_ordens(df):
    df = df.copy()
    colunas = {
        "USUARIO_RESPONSAVEL": _encontrar_coluna(df, ["USU\u00c1RIO RESPONSAVEL", "USUARIO RESPONSAVEL"]),
        "STATUS": _encontrar_coluna(df, ["STATUS"]),
        "OP": _encontrar_coluna(df, ["N\u00b0 DA OP", "N DA OP", "OP"]),
        "COD_PRODUTO": _encontrar_coluna(df, ["COD_PRODUTO", "CODIGO PRODUTO"]),
        "PRODUTO": _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O", "DESCRICAO"]),
        "COD_PECA": _encontrar_coluna(df, ["COD_PE\u00c7A", "COD_PECA"]),
        "PECA": _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O PE\u00c7A", "DESCRICAO PECA"]),
        "QTD_PECAS": _encontrar_coluna(df, ["QTD_PE\u00c7AS", "QTD_PECAS"]),
        "QUANTIDADE": _encontrar_coluna(df, ["QUANTIDADE"]),
        "REALIZADO": _encontrar_coluna(df, ["REALIZADO"]),
        "DATA_ABERTURA": _encontrar_coluna(df, ["DATA_ABERTURA"]),
        "DATA_PREVISTA": _encontrar_coluna(df, ["DATA_PREVISTA"]),
        "DATA": _encontrar_coluna(df, ["DATA"]),
        "OBS": _encontrar_coluna(df, ["OBS", "A\u00c7\u00c3O", "ACAO"]),
    }

    for nome_padrao, coluna_origem in colunas.items():
        if coluna_origem is None:
            df[nome_padrao] = ""
        else:
            df[nome_padrao] = df[coluna_origem].astype(str).str.strip()

    campos_chave = ["OP", "COD_PRODUTO", "PRODUTO", "QUANTIDADE", "REALIZADO", "STATUS", "DATA", "DATA_PREVISTA", "OBS"]
    tem_dados = df[campos_chave].apply(lambda linha: any(str(valor).strip() for valor in linha), axis=1)
    df = df[tem_dados].copy()

    if df.empty:
        return _garantir_colunas(df, COLUNAS_ORDENS)

    df["USUARIO_RESPONSAVEL"] = df["USUARIO_RESPONSAVEL"].replace("", "Sem responsavel")
    df["STATUS"] = df["STATUS"].replace("", "Sem status")
    df["REALIZADO"] = df["REALIZADO"].replace("", "0")
    df["QUANTIDADE_NUM"] = _serie_numero(df["QUANTIDADE"])
    df["REALIZADO_NUM"] = _serie_numero(df["REALIZADO"])
    df["SALDO_NUM"] = (df["QUANTIDADE_NUM"] - df["REALIZADO_NUM"]).clip(lower=0)
    df["DATA_PRIORIDADE"] = pd.to_datetime(df.apply(_data_prioridade, axis=1), errors="coerce")
    df["DIAS_ATRASO"] = (pd.Timestamp.today().normalize() - df["DATA_PRIORIDADE"]).dt.days
    df["ATRASADA"] = (df["DIAS_ATRASO"] > 0) & (df["STATUS"].str.upper() != "OK")

    return _garantir_colunas(df, COLUNAS_ORDENS)


def _vincular_pecas_a_ordem(df):
    if df.empty:
        return df

    df = df.copy()
    coluna_op = _encontrar_coluna(df, ["N\u00b0 DA OP", "N DA OP", "OP"])
    coluna_cod_produto = _encontrar_coluna(df, ["COD_PRODUTO", "CODIGO PRODUTO"])
    coluna_produto = _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O", "DESCRICAO"])
    coluna_cod_peca = _encontrar_coluna(df, ["COD_PE\u00c7A", "COD_PECA"])
    coluna_peca = _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O PE\u00c7A", "DESCRICAO PECA"])
    coluna_qtd_pecas = _encontrar_coluna(df, ["QTD_PE\u00c7AS", "QTD_PECAS"])

    if not all([coluna_op, coluna_cod_produto, coluna_produto]):
        df["PECAS_BLOCO"] = [[] for _ in range(len(df))]
        return df

    pecas_por_linha_mae = {}
    linha_mae_atual = None

    for indice, linha in df.iterrows():
        tem_ordem = any(
            str(linha.get(coluna, "")).strip()
            for coluna in [coluna_op, coluna_cod_produto, coluna_produto]
        )

        if tem_ordem:
            linha_mae_atual = indice
            pecas_por_linha_mae.setdefault(indice, [])

        if linha_mae_atual is None:
            continue

        codigo_peca = str(linha.get(coluna_cod_peca, "")).strip() if coluna_cod_peca else ""
        descricao_peca = str(linha.get(coluna_peca, "")).strip() if coluna_peca else ""
        qtd_pecas = str(linha.get(coluna_qtd_pecas, "")).strip() if coluna_qtd_pecas else ""

        if codigo_peca or descricao_peca or qtd_pecas:
            pecas_por_linha_mae.setdefault(linha_mae_atual, []).append(
                {
                    "Cod. peca": codigo_peca,
                    "Peca faltante": descricao_peca,
                    "Qtd. pecas": qtd_pecas,
                }
            )

    df["PECAS_BLOCO"] = [
        pecas_por_linha_mae.get(indice, [])
        for indice in df.index
    ]
    return df


def _data_prioridade(linha):
    if linha["ABA_ORIGEM"] == "Produ\u00e7\u00e3o":
        texto_data = linha.get("DATA_PREVISTA", "")
    else:
        texto_data = linha.get("DATA", "")

    data = pd.to_datetime(texto_data, dayfirst=True, errors="coerce")
    return data.normalize() if pd.notna(data) else pd.NaT


def _serie_numero(serie):
    return pd.to_numeric(
        serie.fillna("").astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    ).fillna(0)


def _numero_celula(valor):
    numero = pd.to_numeric(str(valor or "").strip().replace(",", "."), errors="coerce")
    return 0 if pd.isna(numero) else float(numero)


def _indice_coluna(headers, nome):
    nome_normalizado = _normalizar(nome)
    for index, header in enumerate(headers, start=1):
        if _normalizar(header) == nome_normalizado:
            return index
    raise ValueError(f"Coluna {nome} nao encontrada.")


def _encontrar_coluna(df, nomes):
    mapa = {_normalizar(coluna): coluna for coluna in df.columns}
    for nome in nomes:
        coluna = mapa.get(_normalizar(nome))
        if coluna:
            return coluna
    return None


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto).strip().upper())
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return "".join(char for char in texto if char.isalnum())


def _formatar_numero(valor):
    valor = float(valor)
    if valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")
