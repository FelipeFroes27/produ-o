from html import escape
from pathlib import Path
import base64

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.display_mode import ativar_modo_exibicao, page_link_icon, render_menu_lateral, render_sidebar_brand
from utils.sheets import _normalizar, acao_base_historico, acao_etapa_historico, carregar_historico, carregar_ordens, carregar_resumo, carregar_usuarios, lancar_inicio_ordem, lancar_pausa_ordem, lancar_realizacao


st.set_page_config(
    page_title="Producao",
    page_icon="icones/producao.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("producao")
render_menu_lateral()

CORES = ["#2563eb", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#06b6d4"]
ICONES_BOTOES = {
    "inicio": "icones/start-up.png",
    "pausa": "icones/pausa.png",
    "consulta": "icones/informacoes.png",
    "conclusao": "icones/verificado.png",
}


def aplicar_estilo():
    st.markdown(
        """
        <style>
        header,
        header[data-testid="stHeader"],
        [data-testid="stStatusWidget"],
        [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        footer, #MainMenu {visibility: hidden;}

        .stApp {
            background: #ffffff;
            color: #000000;
        }

        [data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid #000000;
        }

        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        [data-testid="stSidebar"] a,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        label {
            color: #000000 !important;
        }

        .block-container,
        [data-testid="stMainBlockContainer"] {
            max-width: 1540px;
            padding-top: .45rem;
            padding-bottom: 1.25rem;
        }

        div[data-testid="stVerticalBlock"] {
            gap: .95rem !important;
        }

        .sidebar-logo {
            display: flex;
            gap: 10px;
            align-items: center;
            justify-content: center;
            padding: 18px 16px 22px 16px;
            margin-bottom: 8px;
            border-bottom: 1px solid #e4e4e4;
        }

        .sidebar-logo img {
            background: #ffffff;
            border: 0;
            padding: 0;
            max-height: 42px;
            width: auto;
        }

        .page-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 18px;
            margin-bottom: 10px;
        }

        .page-title h1 {
            margin: 0;
            color: #000000;
            font-size: 28px;
            line-height: 1.05;
            font-weight: 850;
            letter-spacing: 0;
        }

        .page-title p {
            margin: 6px 0 0 0;
            color: #333333;
            font-size: 14px;
        }

        .page-logos {
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 0 0 auto;
        }

        .page-logos img {
            max-height: 36px;
            max-width: 158px;
            object-fit: contain;
        }

        .page-logos .goper-mark {
            max-height: 36px;
            max-width: 36px;
        }

        .logo-divider {
            width: 3px;
            height: 34px;
            background: #000000;
            display: inline-block;
        }

        .user-title {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            min-height: 48px;
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            color: #000000;
            font-size: 27px;
            line-height: 1;
            font-weight: 850;
        }

        .st-key-usuario_anterior button,
        .st-key-usuario_proximo button,
        .st-key-atualizar_ordens button {
            min-height: 42px;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            color: #000000 !important;
            font-weight: 800;
            box-shadow: none !important;
        }

        .st-key-usuario_anterior button:disabled,
        .st-key-usuario_proximo button:disabled,
        .st-key-atualizar_ordens button:disabled {
            border: 2px solid #000000 !important;
            background: #ffffff !important;
            color: #000000 !important;
            opacity: .55 !important;
        }

        .st-key-usuario_anterior button:hover,
        .st-key-usuario_proximo button:hover,
        .st-key-atualizar_ordens button:hover {
            background: #f2f4f7 !important;
            border-color: #000000 !important;
            color: #000000 !important;
        }

        .kpi-card,
        .panel,
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stDataFrame"] {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: none;
        }

        .kpi-card {
            min-height: 104px;
            padding: 14px;
            overflow-wrap: anywhere;
        }

        .kpi-label {
            color: #333333;
            font-size: 13px;
            font-weight: 750;
        }

        .kpi-value {
            margin-top: 5px;
            color: #000000;
            font-size: 28px;
            line-height: 1;
            font-weight: 850;
        }

        .kpi-note {
            margin-top: 7px;
            color: #555555;
            font-size: 12px;
        }

        .panel {
            padding: 14px;
        }

        .panel-title {
            margin: 0 0 10px 0;
            color: #000000;
            font-size: 16px;
            font-weight: 850;
            line-height: 1.15;
        }

        .order-card {
            padding: 2px 0;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-late-marker) {
            background: #fff1f2 !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-late-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-late-marker) {
            background: #fff1f2 !important;
            border: 0 !important;
            border-radius: 0 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-warning-marker) {
            background: #fffbeb !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-warning-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-warning-marker) {
            background: #fffbeb !important;
            border: 0 !important;
            border-radius: 0 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-safe-marker) {
            background: #ecfdf5 !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-safe-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-safe-marker) {
            background: #ecfdf5 !important;
            border: 0 !important;
            border-radius: 0 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-neutral-marker) {
            background: #f8fafc !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-neutral-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-neutral-marker) {
            background: #f8fafc !important;
            border: 0 !important;
            border-radius: 0 !important;
        }

        .risk-late-marker,
        .risk-warning-marker,
        .risk-safe-marker,
        .risk-neutral-marker {
            display: block;
            height: 0;
            width: 0;
            overflow: hidden;
        }

        .order-name {
            color: #000000;
            font-size: 18px;
            line-height: 1.2;
            font-weight: 850;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: normal;
            overflow-wrap: anywhere;
        }

        .order-meta {
            display: block;
            margin-top: 6px;
            color: #333333;
            font-size: 13px;
            line-height: 1.35;
            font-weight: 760;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: normal;
        }

        .order-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }

        .order-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 28px;
            padding: 4px 10px;
            border: 1px solid #000000;
            border-radius: 7px;
            background: #ffffff;
            color: #000000;
            font-size: 12px;
            font-weight: 850;
            white-space: nowrap;
        }

        .duplicate-alert {
            margin-top: 9px;
            display: inline-flex;
            align-items: center;
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffe3e3;
            color: #000000;
            padding: 7px 9px;
            font-size: 12px;
            line-height: 1.2;
            font-weight: 900;
            max-width: 100%;
            white-space: normal;
        }

        .order-number {
            color: #000000;
            font-size: 24px;
            line-height: 1;
            text-align: center;
            font-weight: 850;
        }

        .order-label {
            margin-top: 6px;
            color: #333333;
            font-size: 12px;
            text-align: center;
            font-weight: 800;
            white-space: nowrap;
        }

        .card-actions {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
        }

        .card-action-row {
            display: none;
        }

        .st-key-cards_lista [data-testid="stVerticalBlock"] {
            gap: .3cm !important;
        }

        .st-key-cards_lista [class*="st-key-card_"] {
            margin: 0 !important;
        }

        .status-tag {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 84px;
            padding: 5px 9px;
            border: 1px solid #000000;
            border-radius: 6px;
            background: #ffffff;
            color: #000000;
            font-size: 11px;
            font-weight: 850;
        }

        .empty {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 120px;
            border: 2px dashed #999999;
            border-radius: 8px;
            color: #333333;
            background: #ffffff;
            text-align: center;
            font-weight: 700;
        }

        div[data-testid="stDialog"] div[role="dialog"] {
            width: min(1180px, 94vw) !important;
            max-width: min(1180px, 94vw) !important;
            max-height: 90vh !important;
            overflow-y: auto !important;
            border-radius: 8px !important;
        }

        div[data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
            gap: .55rem !important;
        }

        .detail-grid {
            display: grid;
            grid-template-columns: minmax(0, .9fr) minmax(0, .9fr) minmax(0, 1.15fr) minmax(0, .9fr);
            gap: 8px;
            margin-bottom: 8px;
        }

        .detail-box {
            min-height: 52px;
            padding: 7px 8px;
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            overflow: hidden;
        }

        .detail-label {
            color: #333333;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
        }

        .detail-value {
            margin-top: 5px;
            color: #000000;
            font-size: 14px;
            font-weight: 850;
            overflow-wrap: anywhere;
            line-height: 1.25;
        }

        .obs-box {
            padding: 8px 10px;
            margin: 0 0 8px 0;
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
        }

        .obs-label {
            color: #333333;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
        }

        .obs-value {
            margin-top: 5px;
            color: #000000;
            font-size: 14px;
            line-height: 1.35;
            font-weight: 800;
            overflow-wrap: anywhere;
            max-height: 78px;
            overflow-y: auto;
        }

        div[data-testid="stForm"] {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 10px 12px;
            box-shadow: none !important;
        }

        div[data-testid="stForm"] button {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            color: #000000;
            font-weight: 850;
        }

        div[data-testid="stNumberInput"] input {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            color: #000000 !important;
            font-weight: 850 !important;
            box-shadow: none !important;
        }

        div[data-testid="stNumberInput"] button {
            border-color: #000000 !important;
            color: #000000 !important;
        }

        .completion-box {
            display: block;
            margin-top: 6px;
        }

        .completion-spacer {
            height: 25px;
        }

        @media (max-width: 1000px) {
            .page-head {
                display: block;
            }

            .detail-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .order-card {
                grid-template-columns: 1fr;
            }

            .order-number,
            .order-label {
                text-align: left;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        render_sidebar_brand()
        page_link_icon("app.py", "Inicio", "icones/logo preto goper.png")
        page_link_icon("pages/Criar_OP.py", "Criar OP", "icones/nova_ordem.png")
        page_link_icon("pages/Producao.py", "Producao", "icones/producao.png")
        page_link_icon("pages/Qualidade.py", "Qualidade", "icones/qualidade.png")
        page_link_icon("pages/Embalagens.py", "Embalagens", "icones/embalagem.png")
        page_link_icon("pages/Historico_OP.py", "Histórico OP", "icones/historico.png")
        page_link_icon("pages/Dashboard.py", "Dashboard", "icones/indicadores.png")


def normalizar_status(status):
    return str(status).strip().upper()


def numero(valor):
    valor = float(valor or 0)
    if valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")


def inteiro(valor):
    return int(float(valor or 0))


def origem_chave(origem):
    return {
        "Produ\u00e7\u00e3o": "producao",
        "Manuten\u00e7\u00e3o": "manutencao",
        "Pe\u00e7as": "pecas",
    }.get(str(origem), "ordem")


@st.cache_data(show_spinner=False)
def icone_base64(nome_arquivo):
    return base64.b64encode(Path(nome_arquivo).read_bytes()).decode("utf-8")


def aplicar_icone_botao(key, nome_arquivo):
    imagem = icone_base64(nome_arquivo)
    st.markdown(
        f"""
        <style>
        .st-key-{key} div[data-testid="stButton"] button,
        .st-key-{key} button {{
            background-image: url("data:image/png;base64,{imagem}") !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-size: 44px 44px !important;
            background-color: #ffffff !important;
            border: 4px solid #000000 !important;
            border-radius: 999px !important;
            box-shadow: none !important;
            overflow: hidden !important;
            min-height: 60px !important;
            height: 60px !important;
            max-height: 60px !important;
            min-width: 60px !important;
            width: 60px !important;
            max-width: 60px !important;
            padding: 0 !important;
            color: transparent !important;
            font-size: 0 !important;
            line-height: 0 !important;
        }}
        .st-key-{key} div[data-testid="stButton"] button *,
        .st-key-{key} button * {{
            color: transparent !important;
            font-size: 0 !important;
        }}
        .st-key-{key} div[data-testid="stButton"] button:hover,
        .st-key-{key} button:hover {{
            background-color: #f8fafc !important;
            border-color: #000000 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def aplicar_estilo_card(key, cor):
    st.markdown(
        f"""
        <style>
        .st-key-{key},
        .st-key-{key} > div,
        .st-key-{key}[data-testid="stVerticalBlockBorderWrapper"],
        .st-key-{key}[data-testid="stVerticalBlockBorder"],
        .st-key-{key} [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-{key} [data-testid="stVerticalBlockBorder"],
        .st-key-{key} [data-testid="stVerticalBlock"] {{
            background: {cor} !important;
        }}

        .st-key-{key} {{
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            overflow: hidden !important;
        }}

        .st-key-{key}[data-testid="stVerticalBlockBorderWrapper"],
        .st-key-{key} [data-testid="stVerticalBlockBorderWrapper"] {{
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }}

        .st-key-{key}[data-testid="stVerticalBlockBorder"],
        .st-key-{key} [data-testid="stVerticalBlockBorder"] {{
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def data_texto(data):
    if pd.isna(data):
        return "Sem data"
    return pd.to_datetime(data).strftime("%d/%m/%Y")


def ordenar_demanda(df):
    df = df.copy()
    df["SEM_DATA"] = df["DATA_PRIORIDADE"].isna()
    df["ATRASO_SORT"] = df["DIAS_ATRASO"].fillna(-9999)
    return df.sort_values(
        ["SEM_DATA", "ATRASADA", "DATA_PRIORIDADE", "ATRASO_SORT"],
        ascending=[True, False, True, False],
    )


def classe_ordem(linha, selecionada):
    classes = ["order-card"]
    if bool(linha.get("ATRASADA", False)):
        classes.append("late")
    elif pd.isna(linha.get("DATA_PRIORIDADE")):
        classes.append("neutral")
    elif (linha["DATA_PRIORIDADE"].date() - pd.Timestamp.today().date()).days <= 5:
        classes.append("warning")
    else:
        classes.append("safe")
    if selecionada:
        classes.append("selected")
    return " ".join(classes)


def classe_risco(linha):
    if bool(linha.get("ATRASADA", False)):
        return "risk-late-marker"
    if pd.isna(linha.get("DATA_PRIORIDADE")):
        return "risk-neutral-marker"
    if (linha["DATA_PRIORIDADE"].date() - pd.Timestamp.today().date()).days <= 5:
        return "risk-warning-marker"
    return "risk-safe-marker"


def cor_risco(linha):
    if bool(linha.get("ATRASADA", False)):
        return "#ffdfe3"
    if pd.isna(linha.get("DATA_PRIORIDADE")):
        return "#eef2f7"
    if (linha["DATA_PRIORIDADE"].date() - pd.Timestamp.today().date()).days <= 5:
        return "#fff0bf"
    return "#d9f7e6"


def resumo_prazo(linha):
    if pd.isna(linha["DATA_PRIORIDADE"]):
        return ""
    if bool(linha["ATRASADA"]):
        return f"Atrasada ha {int(linha['DIAS_ATRASO'])} dia(s)"
    if linha["DATA_PRIORIDADE"].date() == pd.Timestamp.today().date():
        return "Para hoje"
    return f"Prazo {data_texto(linha['DATA_PRIORIDADE'])}"


def render_kpi(label, valor, nota):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{escape(label)}</div>
            <div class="kpi-value">{escape(str(valor))}</div>
            <div class="kpi-note">{escape(nota)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def marcar_ordens_em_andamento(ordens, historico):
    ordens = ordens.copy()
    ordens["EM_ANDAMENTO"] = False
    ordens["PAUSADA"] = False
    if ordens.empty or historico.empty or "ACAO" not in historico.columns:
        return ordens

    historico = historico.copy()
    historico["ACAO_NORM"] = historico["ACAO"].map(acao_base_historico)
    historico["ACAO_ETAPA"] = historico["ACAO"].map(acao_etapa_historico)
    historico = historico[
        historico["OP"].astype(str).str.strip().ne("")
        & historico["DATA_HORA_DT"].notna()
        & historico["ACAO_NORM"].isin(["INICIO", "PAUSA", "FIM", "REPROVADO"])
    ].copy()
    if historico.empty:
        return ordens

    chaves_ordem = ["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"]
    chaves_historico = ["TIPO", "OP", "CODIGO", "PRODUTO", "USUARIO_RESPONSAVEL"]
    if not all(coluna in ordens.columns for coluna in chaves_ordem):
        return ordens
    if not all(coluna in historico.columns for coluna in chaves_historico):
        return ordens

    historico["CHAVE_CONTROLE"] = historico[chaves_historico].fillna("").astype(str).apply(
        lambda linha: "|".join(valor.strip().upper() for valor in linha),
        axis=1,
    )
    historico["ETAPA_CONTROLE"] = historico["ACAO_ETAPA"]
    historico.loc[historico["ACAO_NORM"] == "REPROVADO", "ETAPA_CONTROLE"] = historico.loc[
        historico["ACAO_NORM"] == "REPROVADO", "TIPO"
    ].fillna("").astype(str).map(_normalizar)
    historico["TIPO_CONTROLE"] = historico["TIPO"].fillna("").astype(str).map(_normalizar)
    historico = historico[
        historico["ETAPA_CONTROLE"] == historico["TIPO_CONTROLE"]
    ].copy()
    ultima_acao = (
        historico.sort_values("DATA_HORA_DT")
        .groupby("CHAVE_CONTROLE", dropna=False)["ACAO_NORM"]
        .last()
        .to_dict()
    )
    ordens["CHAVE_CONTROLE"] = ordens[chaves_ordem].fillna("").astype(str).apply(
        lambda linha: "|".join(valor.strip().upper() for valor in linha),
        axis=1,
    )
    ordens["ULTIMA_ACAO_CONTROLE"] = ordens["CHAVE_CONTROLE"].map(ultima_acao).fillna("")
    ordens["EM_ANDAMENTO"] = (ordens["ULTIMA_ACAO_CONTROLE"] == "INICIO") & (ordens["SALDO_NUM"] > 0)
    ordens["PAUSADA"] = (ordens["ULTIMA_ACAO_CONTROLE"] == "PAUSA") & (ordens["SALDO_NUM"] > 0)
    return ordens


def marcar_ordens_duplicadas(ordens):
    ordens = ordens.copy()
    ordens["DUPLICADA_PROGRAMACAO"] = False
    ordens["QTD_DUPLICADAS_PROGRAMACAO"] = 1
    if ordens.empty:
        return ordens

    chaves = ["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"]
    for coluna in chaves:
        if coluna not in ordens.columns:
            return ordens

    chave_normalizada = ordens[chaves].fillna("").astype(str).apply(lambda coluna: coluna.str.strip().str.upper())
    contagem = chave_normalizada.groupby(chaves, dropna=False).transform("size")
    ordens["DUPLICADA_PROGRAMACAO"] = contagem > 1
    ordens["QTD_DUPLICADAS_PROGRAMACAO"] = contagem
    return ordens


def ocultar_repeticoes_duplicadas(ordens):
    if ordens.empty or "DUPLICADA_PROGRAMACAO" not in ordens.columns:
        return ordens

    chaves = ["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"]
    if not all(coluna in ordens.columns for coluna in chaves):
        return ordens

    duplicadas = ordens[ordens["DUPLICADA_PROGRAMACAO"]].drop_duplicates(subset=chaves, keep="first")
    normais = ordens[~ordens["DUPLICADA_PROGRAMACAO"]]
    return pd.concat([normais, duplicadas], ignore_index=True, sort=False)


def render_ordem_card(linha, ordens_usuario):
    chave = f"{linha['ABA_ORIGEM']}|{linha['LINHA_PLANILHA']}"
    chave_css = f"{origem_chave(linha['ABA_ORIGEM'])}_{linha['LINHA_PLANILHA']}"
    key_card = f"card_{chave_css}"
    produto = str(linha["PRODUTO"]) or "Produto sem descricao"
    op = str(linha["OP"]) or "Sem OP"
    codigo = str(linha["COD_PRODUTO"]) or "Sem codigo"
    status = str(linha["STATUS"]) or "Sem status"
    em_andamento = bool(linha.get("EM_ANDAMENTO", False))
    pausada = bool(linha.get("PAUSADA", False))
    duplicada = bool(linha.get("DUPLICADA_PROGRAMACAO", False))
    qtd_duplicadas = int(linha.get("QTD_DUPLICADAS_PROGRAMACAO", 1) or 1)
    status_exibido = "PAUSADO" if pausada else status
    badges = [
        f'<span class="order-badge">Qtd. {escape(numero(linha["QUANTIDADE_NUM"]))}</span>',
        f'<span class="order-badge">Realizado {escape(numero(linha["REALIZADO_NUM"]))}</span>',
        f'<span class="order-badge">Status {escape(status_exibido)}</span>',
    ]
    if em_andamento:
        badges.append('<span class="order-badge">Em andamento</span>')
    if pausada:
        badges.append('<span class="order-badge">Pausado</span>')
    badges_html = "".join(badges)
    alerta_duplicidade = (
        f'<div class="duplicate-alert">Esta ordem esta em {qtd_duplicadas} linhas na programacao. Corrija a planilha para liberar inicio/conclusao.</div>'
        if duplicada
        else ""
    )
    aplicar_estilo_card(key_card, cor_risco(linha))
    with st.container(border=True, key=key_card):
        st.markdown(f'<span class="{classe_risco(linha)}"></span>', unsafe_allow_html=True)
        col_info, col_saldo, col_acoes = st.columns([6.55, .85, 1.7], vertical_alignment="center")

        with col_info:
            st.markdown(
                f"""
                <div class="order-card">
                    <div class="order-name" title="{escape(produto)}">Ordem - {escape(op)} | {escape(produto)}</div>
                    <span class="order-meta">
                        {escape(str(linha["ABA_ORIGEM"]))} | Cod. {escape(codigo)} | {escape(resumo_prazo(linha))}
                    </span>
                    <div class="order-badges">
                        {badges_html}
                    </div>
                    {alerta_duplicidade}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_saldo:
            st.markdown(
                f"""
                <div>
                    <div class="order-number">{escape(numero(linha["SALDO_NUM"]))}</div>
                    <div class="order-label">saldo</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_acoes:
            acao_1, acao_2, acao_3, acao_4 = st.columns(4, gap="small")
            with acao_1:
                key_inicio = f"inicio_{chave_css}"
                trava_inicio = f"trava_{key_inicio}"
                aplicar_icone_botao(key_inicio, ICONES_BOTOES["inicio"])
                st.markdown('<div class="start-button">', unsafe_allow_html=True)
                inicio_desabilitado = duplicada or (em_andamento and not pausada) or bool(st.session_state.get(trava_inicio, False))
                texto_inicio = "Retomar" if pausada else "Iniciar"
                ajuda_inicio = (
                    "Corrija a duplicidade na programacao para iniciar."
                    if duplicada
                    else "A ordem ja esta em andamento."
                    if em_andamento and not pausada
                    else "Retomar contagem da ordem."
                    if pausada
                    else "Registrar inicio da ordem."
                )
                if st.button(texto_inicio, key=key_inicio, help=ajuda_inicio, disabled=inicio_desabilitado):
                    if st.session_state.get(trava_inicio, False):
                        st.warning("Lancamento ja esta em andamento.")
                        st.markdown("</div>", unsafe_allow_html=True)
                        return
                    st.session_state[trava_inicio] = True
                    try:
                        lancar_inicio_ordem(linha)
                    except Exception as exc:
                        st.session_state.pop(trava_inicio, None)
                        st.error(str(exc))
                    else:
                        st.session_state.pop(trava_inicio, None)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with acao_2:
                key_pausa = f"pausa_{chave_css}"
                trava_pausa = f"trava_{key_pausa}"
                aplicar_icone_botao(key_pausa, ICONES_BOTOES["pausa"])
                st.markdown('<div class="pause-button">', unsafe_allow_html=True)
                pausa_desabilitada = duplicada or pausada or not em_andamento or bool(st.session_state.get(trava_pausa, False))
                ajuda_pausa = (
                    "Corrija a duplicidade na programacao para pausar."
                    if duplicada
                    else "A ordem ja esta pausada."
                    if pausada
                    else "A ordem precisa estar em andamento para pausar."
                    if not em_andamento
                    else "Pausar contagem da ordem."
                )
                if st.button("Pausar", key=key_pausa, help=ajuda_pausa, disabled=pausa_desabilitada):
                    if st.session_state.get(trava_pausa, False):
                        st.warning("Lancamento ja esta em andamento.")
                        st.markdown("</div>", unsafe_allow_html=True)
                        return
                    st.session_state[trava_pausa] = True
                    try:
                        lancar_pausa_ordem(linha)
                    except Exception as exc:
                        st.session_state.pop(trava_pausa, None)
                        st.error(str(exc))
                    else:
                        st.session_state.pop(trava_pausa, None)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with acao_3:
                key_consulta = f"consulta_{chave_css}"
                aplicar_icone_botao(key_consulta, ICONES_BOTOES["consulta"])
                st.markdown('<div class="consult-button">', unsafe_allow_html=True)
                if st.button("Consultar", key=key_consulta, help="Consultar ordem"):
                    modal_consulta(linha, ordens_usuario)
                st.markdown("</div>", unsafe_allow_html=True)
            with acao_4:
                key_conclusao = f"conclusao_{chave_css}"
                aplicar_icone_botao(key_conclusao, ICONES_BOTOES["conclusao"])
                st.markdown('<div class="finish-button">', unsafe_allow_html=True)
                conclusao_desabilitada = duplicada or pausada or not em_andamento
                ajuda_conclusao = (
                    "Corrija a duplicidade na programacao para concluir."
                    if duplicada
                    else "Retome a ordem antes de concluir."
                    if pausada
                    else "Inicie a ordem antes de concluir."
                    if not em_andamento
                    else "Concluir ordem"
                )
                if st.button("Concluir", key=key_conclusao, help=ajuda_conclusao, disabled=conclusao_desabilitada):
                    modal_conclusao(linha, ordens_usuario)
                st.markdown("</div>", unsafe_allow_html=True)


def render_ordem_card_antigo(linha):
    chave = f"{linha['ABA_ORIGEM']}|{linha['LINHA_PLANILHA']}"
    selecionada = st.session_state.get("ordem_selecionada") == chave
    produto = str(linha["PRODUTO"]) or "Produto sem descricao"
    op = str(linha["OP"]) or "Sem OP"
    codigo = str(linha["COD_PRODUTO"]) or "Sem codigo"

    st.markdown(
        f"""
        <div class="{classe_ordem(linha, selecionada)}">
            <div>
                <div class="order-name" title="{escape(produto)}">{escape(produto)}</div>
                <span class="order-meta">
                    {escape(str(linha["ABA_ORIGEM"]))} | OP {escape(op)} | Cod. {escape(codigo)}
                </span>
                <span class="order-meta">{escape(resumo_prazo(linha))}</span>
            </div>
            <div>
                <div class="order-number">{escape(numero(linha["SALDO_NUM"]))}</div>
                <div class="order-label">saldo</div>
            </div>
            <div>
                <div class="order-number">{escape(numero(linha["QUANTIDADE_NUM"]))}</div>
                <div class="order-label">total</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="order-action">', unsafe_allow_html=True)
    if st.button("Abrir ordem", key=f"abrir_{chave}", use_container_width=True):
        st.session_state.ordem_selecionada = chave
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def rotulo_ordem(linha):
    op = str(linha["OP"]) or "Sem OP"
    codigo = str(linha["COD_PRODUTO"]) or "Sem codigo"
    produto = str(linha["PRODUTO"]) or "Produto sem descricao"
    return f"{linha['ABA_ORIGEM']} | OP {op} | {codigo} | {produto[:70]}"


def localizar_ordem(df):
    chave = st.session_state.get("ordem_selecionada")
    if not chave:
        return None
    aba, linha = chave.split("|", 1)
    encontrados = df[(df["ABA_ORIGEM"] == aba) & (df["LINHA_PLANILHA"].astype(str) == linha)]
    if encontrados.empty:
        return None
    return encontrados.iloc[0]


def render_detalhe(ordem, ordens_usuario, modo="consulta"):
    if ordem is None:
        st.markdown('<div class="empty">Selecione uma ordem na lista para ver os detalhes e lancar a realizacao.</div>', unsafe_allow_html=True)
        return

    titulo = "Consulta da ordem" if modo == "consulta" else "Conclusao da ordem"
    st.markdown(f'<div class="panel"><div class="panel-title">{titulo}</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="detail-grid">
            <div class="detail-box">
                <div class="detail-label">Origem</div>
                <div class="detail-value">{escape(str(ordem["ABA_ORIGEM"]))}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">OP</div>
                <div class="detail-value">{escape(str(ordem["OP"]) or "Sem OP")}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Codigo</div>
                <div class="detail-value">{escape(str(ordem["COD_PRODUTO"]) or "Sem codigo")}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Status</div>
                <div class="detail-value"><span class="status-tag">{escape(str(ordem["STATUS"]))}</span></div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Produto</div>
                <div class="detail-value">{escape(str(ordem["PRODUTO"]) or "-")}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Prazo</div>
                <div class="detail-value">{escape(resumo_prazo(ordem))}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Realizado</div>
                <div class="detail-value">{escape(numero(ordem["REALIZADO_NUM"]))} de {escape(numero(ordem["QUANTIDADE_NUM"]))}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Saldo</div>
                <div class="detail-value">{escape(numero(ordem["SALDO_NUM"]))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    observacao = str(ordem["OBS"]).strip() or "-"
    st.markdown(
        f"""
        <div class="obs-box">
            <div class="obs-label">Observacoes</div>
            <div class="obs-value">{escape(observacao)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if ordem["ABA_ORIGEM"] == "Pe\u00e7as":
        render_pecas_faltantes(ordem, ordens_usuario)

    if modo == "conclusao":
        saldo = float(ordem["SALDO_NUM"])
        if saldo <= 0:
            st.success("Esta ordem nao possui saldo pendente.")
        elif not bool(ordem.get("EM_ANDAMENTO", False)):
            if bool(ordem.get("PAUSADA", False)):
                st.warning("Retome a ordem antes de concluir.")
            else:
                st.warning("Inicie a ordem antes de concluir.")
        else:
            chave_lancamento = f"{ordem['ABA_ORIGEM']}_{ordem['LINHA_PLANILHA']}"
            trava_lancamento = f"lancamento_em_andamento_{chave_lancamento}"
            lancamento_em_andamento = bool(st.session_state.get(trava_lancamento, False))
            st.markdown('<div class="completion-box">', unsafe_allow_html=True)
            with st.form(f"form_lancamento_{chave_lancamento}"):
                qtd_col, flag_col, botao_col = st.columns([1, .65, 1])
                with qtd_col:
                    quantidade = st.number_input(
                        "Quantidade realizada agora",
                        min_value=1,
                        max_value=max(1, inteiro(saldo)),
                        step=1,
                        value=min(1, inteiro(saldo)),
                        help="O valor sera somado ao realizado atual da ordem.",
                    )
                with flag_col:
                    st.markdown('<div class="completion-spacer"></div>', unsafe_allow_html=True)
                    enviar_qualidade = st.checkbox(
                        "Qualidade",
                        key=f"qualidade_{chave_lancamento}",
                        help="Enviar este lancamento para aprovacao da qualidade.",
                    )
                with botao_col:
                    st.markdown('<div class="completion-spacer"></div>', unsafe_allow_html=True)
                    confirmar = st.form_submit_button(
                        "Lancamento em andamento..." if lancamento_em_andamento else "Confirmar realizacao",
                        use_container_width=True,
                        disabled=lancamento_em_andamento,
                    )
            st.markdown('</div>', unsafe_allow_html=True)

            if confirmar:
                if st.session_state.get(trava_lancamento, False):
                    st.warning("Lancamento ja esta em andamento.")
                    return
                st.session_state[trava_lancamento] = True
                try:
                    lancar_realizacao(ordem, quantidade, qualidade=enviar_qualidade)
                except Exception as exc:
                    st.session_state.pop(trava_lancamento, None)
                    st.error(str(exc))
                else:
                    st.success("Realizacao registrada na ordem e no historico.")
                    st.session_state.pop(trava_lancamento, None)
                    st.session_state.pop("ordem_selecionada", None)
                    st.session_state.pop("acao_ordem", None)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("Consulta da ordem", width="large")
def modal_consulta(ordem, ordens_usuario):
    render_detalhe(ordem, ordens_usuario, modo="consulta")


@st.dialog("Concluir ordem", width="large")
def modal_conclusao(ordem, ordens_usuario):
    render_detalhe(ordem, ordens_usuario, modo="conclusao")


def render_pecas_faltantes(ordem, ordens_usuario):
    pecas_bloco = ordem.get("PECAS_BLOCO", [])
    if not pecas_bloco:
        return

    pecas = pd.DataFrame(pecas_bloco)
    st.markdown('<div class="panel-title">Pecas faltantes para consulta</div>', unsafe_allow_html=True)
    altura = min(220, 42 + (len(pecas) * 32))
    st.dataframe(pecas, use_container_width=True, hide_index=True, height=max(110, altura))


def grafico_por_aba(ordens_usuario):
    contagem = (
        ordens_usuario.groupby("ABA_ORIGEM")
        .size()
        .reset_index(name="Ordens")
        .rename(columns={"ABA_ORIGEM": "Origem"})
    )
    fig = px.bar(contagem, x="Origem", y="Ordens", color="Origem", color_discrete_sequence=CORES)
    fig.update_layout(
        height=260,
        margin=dict(l=8, r=8, t=8, b=8),
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#000000"),
    )
    fig.update_traces(marker_line_color="#000000", marker_line_width=2)
    fig.update_xaxes(showgrid=False, linecolor="#000000")
    fig.update_yaxes(gridcolor="#e5e7eb", linecolor="#000000", rangemode="tozero")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


aplicar_estilo()
render_sidebar()

logo_branco = base64.b64encode(Path("icones/Logo Branco.bmp").read_bytes()).decode("utf-8")
logo_goper = base64.b64encode(Path("icones/logo preto goper.png").read_bytes()).decode("utf-8")

st.markdown(
    f"""
    <div class="page-head">
        <div class="page-title">
            <h1>Ordens do usuario</h1>
            <p>Demanda de trabalho por responsavel, priorizada por prazo e saldo pendente.</p>
        </div>
        <div class="page-logos">
            <img src="data:image/bmp;base64,{logo_branco}" alt="Trendx">
            <span class="logo-divider"></span>
            <img class="goper-mark" src="data:image/png;base64,{logo_goper}" alt="Goper">
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    usuarios, ordens = carregar_resumo()
    historico = carregar_historico()
    ordens = marcar_ordens_em_andamento(ordens, historico)
except Exception as exc:
    st.error("Nao foi possivel carregar a planilha Planejamento Producao.")
    st.caption(str(exc))
    st.stop()

if usuarios.empty:
    st.warning("Nenhum usuario cadastrado na aba Usuarios.")
    st.stop()

nomes_usuarios = sorted(usuarios["Nome"].dropna().astype(str).str.strip().loc[lambda serie: serie != ""].unique())
if not nomes_usuarios:
    st.warning("Nenhum usuario com nome preenchido.")
    st.stop()

if "usuario_idx" not in st.session_state:
    st.session_state.usuario_idx = 0
st.session_state.usuario_idx = min(st.session_state.usuario_idx, len(nomes_usuarios) - 1)

nav_1, nav_2, nav_3, nav_4 = st.columns([.55, 3.1, .55, .8])
with nav_1:
    st.markdown('<div class="nav-button">', unsafe_allow_html=True)
    if st.button("<", key="usuario_anterior", use_container_width=True, disabled=st.session_state.usuario_idx <= 0):
        st.session_state.usuario_idx -= 1
        st.session_state.pop("ordem_selecionada", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

usuario_atual = nomes_usuarios[st.session_state.usuario_idx]
with nav_2:
    st.markdown(f'<div class="user-title">{escape(usuario_atual)}</div>', unsafe_allow_html=True)

with nav_3:
    st.markdown('<div class="nav-button">', unsafe_allow_html=True)
    if st.button(">", key="usuario_proximo", use_container_width=True, disabled=st.session_state.usuario_idx >= len(nomes_usuarios) - 1):
        st.session_state.usuario_idx += 1
        st.session_state.pop("ordem_selecionada", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with nav_4:
    st.markdown('<div class="refresh-button">', unsafe_allow_html=True)
    if st.button("Atualizar", key="atualizar_ordens", use_container_width=True):
        carregar_usuarios.clear()
        carregar_ordens.clear()
        carregar_historico.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

ordens_pendentes = ordens[
    (ordens["USUARIO_RESPONSAVEL"].astype(str).str.strip() == usuario_atual)
    & (ordens["STATUS"].astype(str).str.upper() != "OK")
    & (ordens["SALDO_NUM"] > 0)
    & (ordens["DATA_PRIORIDADE"].notna())
    & (ordens["OP"].astype(str).str.strip() != "")
].copy()
ordens_pendentes = marcar_ordens_duplicadas(ordens_pendentes)
ordens_pendentes = ordenar_demanda(ordens_pendentes)
ordens_exibicao = ordenar_demanda(ocultar_repeticoes_duplicadas(ordens_pendentes))

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi("Ordens pendentes", len(ordens_exibicao), "Demandas abertas para este usuario")
with k2:
    render_kpi("Atrasadas", int(ordens_exibicao["ATRASADA"].sum()) if not ordens_exibicao.empty else 0, "Status pendente com data vencida")
with k3:
    producao = int((ordens_exibicao["ABA_ORIGEM"] == "Produ\u00e7\u00e3o").sum()) if not ordens_exibicao.empty else 0
    render_kpi("Producao", producao, "Produtos novos para montar")
with k4:
    manutencao_pecas = int(ordens_exibicao["ABA_ORIGEM"].isin(["Manuten\u00e7\u00e3o", "Pe\u00e7as"]).sum()) if not ordens_exibicao.empty else 0
    render_kpi("Manutencao e pecas", manutencao_pecas, "Demandas de reparo ou falta de pecas")

st.markdown('<div class="panel-title">Demandas do usuario</div>', unsafe_allow_html=True)
if ordens_exibicao.empty:
    st.markdown('<div class="empty">Nada pendente para este usuario.</div>', unsafe_allow_html=True)
else:
    with st.container(key="cards_lista"):
        for _, linha in ordens_exibicao.iterrows():
            render_ordem_card(linha, ordens_pendentes)
