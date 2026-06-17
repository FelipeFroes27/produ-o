from html import escape
from pathlib import Path
import base64

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.display_mode import ativar_modo_exibicao, render_menu_lateral
from utils.sheets import carregar_historico, carregar_ordens, carregar_resumo, carregar_usuarios, lancar_inicio_ordem, lancar_realizacao


st.set_page_config(
    page_title="Producao",
    page_icon="icones/consulta-logo-refinado.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("producao")
render_menu_lateral()

CORES = ["#2563eb", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#06b6d4"]
ICONES_BOTOES = {
    "inicio": "start-up.png",
    "consulta": "informacoes.png",
    "conclusao": "verificado.png",
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
            gap: 8px;
            align-items: center;
            justify-content: center;
            padding: 8px 0 16px 0;
        }

        .sidebar-logo img {
            background: #ffffff;
            border: 0;
            padding: 0;
            max-height: 24px;
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
            border-radius: 14px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-late-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-late-marker) {
            background: #fff1f2 !important;
            border-color: #000000 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-warning-marker) {
            background: #fffbeb !important;
            border: 2px solid #000000 !important;
            border-radius: 14px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-warning-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-warning-marker) {
            background: #fffbeb !important;
            border-color: #000000 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-safe-marker) {
            background: #ecfdf5 !important;
            border: 2px solid #000000 !important;
            border-radius: 14px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-safe-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-safe-marker) {
            background: #ecfdf5 !important;
            border-color: #000000 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-neutral-marker) {
            background: #f8fafc !important;
            border: 2px solid #000000 !important;
            border-radius: 14px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.risk-neutral-marker) > div,
        div[data-testid="stVerticalBlockBorder"]:has(.risk-neutral-marker) {
            background: #f8fafc !important;
            border-color: #000000 !important;
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
            border-radius: 12px !important;
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
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        st.image("Logo Branco.bmp", width=72)
        st.image("logo preto goper.png", width=32)
        st.markdown("</div>", unsafe_allow_html=True)
        st.page_link("app.py", label="Inicio")
        st.page_link("pages/Producao.py", label="Producao")
        st.page_link("pages/Dashboard.py", label="Dashboard")


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


def icone_base64(nome_arquivo):
    return base64.b64encode(Path(nome_arquivo).read_bytes()).decode("utf-8")


def aplicar_icone_botao(key, nome_arquivo):
    imagem = icone_base64(nome_arquivo)
    st.markdown(
        f"""
        <style>
        .st-key-{key} button {{
            background-image: url("data:image/png;base64,{imagem}") !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-size: 44px 44px !important;
            background-color: #ffffff !important;
            border: 4px solid #000000 !important;
            border-radius: 999px !important;
            box-shadow: none !important;
            min-height: 60px !important;
            width: 60px !important;
            padding: 0 !important;
            color: transparent !important;
            font-size: 0 !important;
        }}
        .st-key-{key} button * {{
            color: transparent !important;
            font-size: 0 !important;
        }}
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
        .st-key-{key} [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-{key} [data-testid="stVerticalBlockBorder"],
        .st-key-{key} [data-testid="stVerticalBlock"] {{
            background: {cor} !important;
            border-color: #000000 !important;
        }}

        .st-key-{key} [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-{key} [data-testid="stVerticalBlockBorder"] {{
            border: 2px solid #000000 !important;
            border-radius: 14px !important;
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
    if ordens.empty or historico.empty or "ACAO" not in historico.columns:
        return ordens

    historico = historico.copy()
    historico["ACAO_NORM"] = historico["ACAO"].fillna("").astype(str).str.strip().str.upper()
    historico = historico[
        historico["OP"].astype(str).str.strip().ne("")
        & historico["DATA_HORA_DT"].notna()
        & (historico["ACAO_NORM"] == "INICIO")
    ].copy()
    if historico.empty:
        return ordens

    em_andamento_ops = historico["OP"].astype(str).str.strip().unique().tolist()

    if not em_andamento_ops:
        return ordens

    ordens["EM_ANDAMENTO"] = (
        ordens["OP"].astype(str).str.strip().isin(em_andamento_ops)
        & (ordens["SALDO_NUM"] > 0)
    )
    return ordens


def render_ordem_card(linha, ordens_usuario):
    chave = f"{linha['ABA_ORIGEM']}|{linha['LINHA_PLANILHA']}"
    chave_css = f"{origem_chave(linha['ABA_ORIGEM'])}_{linha['LINHA_PLANILHA']}"
    key_card = f"card_{chave_css}"
    produto = str(linha["PRODUTO"]) or "Produto sem descricao"
    op = str(linha["OP"]) or "Sem OP"
    codigo = str(linha["COD_PRODUTO"]) or "Sem codigo"
    status = str(linha["STATUS"]) or "Sem status"
    em_andamento = bool(linha.get("EM_ANDAMENTO", False))
    badges = [
        f'<span class="order-badge">Qtd. {escape(numero(linha["QUANTIDADE_NUM"]))}</span>',
        f'<span class="order-badge">Realizado {escape(numero(linha["REALIZADO_NUM"]))}</span>',
        f'<span class="order-badge">Status {escape(status)}</span>',
    ]
    if em_andamento:
        badges.append('<span class="order-badge">Em andamento</span>')
    badges_html = "".join(badges)
    aplicar_estilo_card(key_card, cor_risco(linha))
    with st.container(border=True, key=key_card):
        st.markdown(f'<span class="{classe_risco(linha)}"></span>', unsafe_allow_html=True)
        col_info, col_saldo, col_acoes = st.columns([7.2, .9, .95], vertical_alignment="center")

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
            acao_1, acao_2, acao_3 = st.columns(3, gap="small")
            with acao_1:
                key_inicio = f"inicio_{chave_css}"
                aplicar_icone_botao(key_inicio, ICONES_BOTOES["inicio"])
                st.markdown('<div class="start-button">', unsafe_allow_html=True)
                if st.button("Iniciar", key=key_inicio, help="Registrar inicio da ordem"):
                    try:
                        lancar_inicio_ordem(linha)
                    except Exception as exc:
                        st.error(str(exc))
                    else:
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with acao_2:
                key_consulta = f"consulta_{chave_css}"
                aplicar_icone_botao(key_consulta, ICONES_BOTOES["consulta"])
                st.markdown('<div class="consult-button">', unsafe_allow_html=True)
                if st.button("Consultar", key=key_consulta, help="Consultar ordem"):
                    modal_consulta(linha, ordens_usuario)
                st.markdown("</div>", unsafe_allow_html=True)
            with acao_3:
                key_conclusao = f"conclusao_{chave_css}"
                aplicar_icone_botao(key_conclusao, ICONES_BOTOES["conclusao"])
                st.markdown('<div class="finish-button">', unsafe_allow_html=True)
                if st.button("Concluir", key=key_conclusao, help="Concluir ordem"):
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
        else:
            st.markdown('<div class="completion-box">', unsafe_allow_html=True)
            with st.form(f"form_lancamento_{ordem['ABA_ORIGEM']}_{ordem['LINHA_PLANILHA']}"):
                qtd_col, botao_col = st.columns([1, 1])
                with qtd_col:
                    quantidade = st.number_input(
                        "Quantidade realizada agora",
                        min_value=1,
                        max_value=max(1, inteiro(saldo)),
                        step=1,
                        value=min(1, inteiro(saldo)),
                        help="O valor sera somado ao realizado atual da ordem.",
                    )
                with botao_col:
                    st.markdown('<div class="completion-spacer"></div>', unsafe_allow_html=True)
                    confirmar = st.form_submit_button("Confirmar realizacao", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if confirmar:
                try:
                    lancar_realizacao(ordem, quantidade)
                except Exception as exc:
                    st.error(str(exc))
                else:
                    st.success("Realizacao registrada na ordem e no historico.")
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

st.markdown(
    """
    <div class="page-head">
        <div class="page-title">
            <h1>Ordens do usuario</h1>
            <p>Demanda de trabalho por responsavel, priorizada por prazo e saldo pendente.</p>
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
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

ordens_pendentes = ordens[
    (ordens["USUARIO_RESPONSAVEL"].astype(str).str.strip() == usuario_atual)
    & (ordens["STATUS"].astype(str).str.upper() != "OK")
    & (ordens["SALDO_NUM"] > 0)
    & (ordens["DATA_PRIORIDADE"].notna())
    & (ordens["OP"].astype(str).str.strip() != "")
].copy()
ordens_pendentes = ordenar_demanda(ordens_pendentes)

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi("Ordens pendentes", len(ordens_pendentes), "Demandas abertas para este usuario")
with k2:
    render_kpi("Atrasadas", int(ordens_pendentes["ATRASADA"].sum()) if not ordens_pendentes.empty else 0, "Status pendente com data vencida")
with k3:
    producao = int((ordens_pendentes["ABA_ORIGEM"] == "Produ\u00e7\u00e3o").sum()) if not ordens_pendentes.empty else 0
    render_kpi("Producao", producao, "Produtos novos para montar")
with k4:
    manutencao_pecas = int(ordens_pendentes["ABA_ORIGEM"].isin(["Manuten\u00e7\u00e3o", "Pe\u00e7as"]).sum()) if not ordens_pendentes.empty else 0
    render_kpi("Manutencao e pecas", manutencao_pecas, "Demandas de reparo ou falta de pecas")

st.markdown('<div class="panel-title">Demandas do usuario</div>', unsafe_allow_html=True)
if ordens_pendentes.empty:
    st.markdown('<div class="empty">Nada pendente para este usuario.</div>', unsafe_allow_html=True)
else:
    with st.container(key="cards_lista"):
        for _, linha in ordens_pendentes.iterrows():
            render_ordem_card(linha, ordens_pendentes)
