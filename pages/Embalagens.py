from html import escape
from pathlib import Path
import base64
import re

import pandas as pd
import streamlit as st

from utils.display_mode import ativar_modo_exibicao, render_menu_lateral
from utils.sheets import (
    acao_base_historico,
    acao_etapa_historico,
    carregar_historico,
    carregar_ordens,
    carregar_usuarios,
    lancar_conclusao_embalagem,
    lancar_encaminhamento_embalagem,
    lancar_inicio_embalagem,
    lancar_pausa_embalagem,
)


st.set_page_config(
    page_title="Embalagens",
    page_icon="icones/consulta-logo-refinado.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("embalagens")
render_menu_lateral()

ICONES_BOTOES = {
    "inicio": "start-up.png",
    "pausa": "pausa.png",
    "conclusao": "verificado.png",
    "consulta": "informacoes.png",
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
            gap: 20px;
            margin: 2.7rem 0 1rem 0;
        }

        .page-head h1 {
            margin: 0 0 .25rem 0;
            color: #000000;
            font-size: 30px;
            line-height: 1.05;
            font-weight: 900;
            letter-spacing: 0;
        }

        .page-head p {
            margin: 0;
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

        .kpi-card {
            min-height: 96px;
            padding: 14px;
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
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

        .panel-title {
            margin: 0 0 10px 0;
            color: #000000;
            font-size: 16px;
            font-weight: 850;
            line-height: 1.15;
        }

        .order-name {
            margin: 0;
            color: #000000;
            font-size: 18px;
            line-height: 1.2;
            font-weight: 900;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .order-meta {
            display: block;
            margin-top: 6px;
            color: #333333;
            font-size: 13px;
            line-height: 1.35;
            font-weight: 760;
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

        .detail-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
            margin-bottom: 10px;
        }

        .detail-box,
        .obs-box {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 10px;
        }

        .detail-label,
        .obs-label {
            font-size: 11px;
            color: #333333;
            font-weight: 850;
            text-transform: uppercase;
        }

        .detail-value,
        .obs-value {
            margin-top: 7px;
            color: #000000;
            font-size: 14px;
            font-weight: 850;
            overflow-wrap: anywhere;
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
        st.page_link("pages/Qualidade.py", label="Qualidade")
        st.page_link("pages/Embalagens.py", label="Embalagens")
        st.page_link("pages/Historico_OP.py", label="Historico OP")
        st.page_link("pages/Dashboard.py", label="Dashboard")


def numero(valor):
    valor = float(valor or 0)
    if valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")


def inteiro(valor):
    return int(float(valor or 0))


def chave_texto(valor):
    return str(valor or "").strip().upper()


def chave_css_texto(*valores):
    bruto = "_".join(chave_texto(valor) for valor in valores)
    chave = re.sub(r"[^A-Z0-9_]+", "_", bruto)
    return chave.strip("_") or "embalagem"


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


def usuarios_embalagem(usuarios):
    if usuarios.empty or "Nome" not in usuarios.columns:
        return []
    return sorted(
        usuarios["Nome"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda serie: serie.ne("")]
        .unique()
        .tolist()
    )


def chave_produto(df):
    return df[["COD_PRODUTO", "PRODUTO"]].fillna("").astype(str).apply(
        lambda linha: "|".join(chave_texto(valor) for valor in linha),
        axis=1,
    )


def chave_fluxo(df):
    return df[["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"]].fillna("").astype(str).apply(
        lambda linha: "|".join(chave_texto(valor) for valor in linha),
        axis=1,
    )


def montar_ordem_embalagem(linha):
    return {
        "USUARIO_RESPONSAVEL": "",
        "OP": "",
        "COD_PRODUTO": str(linha.get("COD_PRODUTO", "")),
        "PRODUTO": str(linha.get("PRODUTO", "")),
        "ABA_ORIGEM": "Embalagem",
        "QUANTIDADE_PENDENTE": float(linha.get("QUANTIDADE_PENDENTE", 0) or 0),
        "QUANTIDADE_NUM": float(linha.get("QUANTIDADE_PENDENTE", 0) or 0),
        "REALIZADO_NUM": 0,
        "SALDO_NUM": 0,
        "STATUS": "",
        "OBS": "",
    }


def montar_fila_embalagem(historico):
    colunas = [
        "COD_PRODUTO",
        "PRODUTO",
        "QUANTIDADE_PENDENTE",
        "QUANTIDADE_SOLICITADA",
        "QUANTIDADE_EMBALADA",
        "DATA_HORA_DT",
        "EM_ANDAMENTO",
        "PAUSADA",
    ]
    if historico.empty or "ACAO" not in historico.columns:
        return pd.DataFrame(columns=colunas)

    dados = historico.copy()
    dados["ACAO_NORM"] = dados["ACAO"].map(acao_base_historico)
    dados["ACAO_ETAPA"] = dados["ACAO"].map(acao_etapa_historico)
    dados["QUANTIDADE_NUM"] = pd.to_numeric(dados["QUANTIDADE_NUM"], errors="coerce").fillna(0)
    dados = dados[dados["CODIGO"].astype(str).str.strip().ne("") | dados["PRODUTO"].astype(str).str.strip().ne("")].copy()
    if dados.empty:
        return pd.DataFrame(columns=colunas)

    entradas = (
        dados[
            (dados["ACAO_NORM"] == "ENTRADA")
            & (dados["ACAO_ETAPA"] == "EMBALAGEM")
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .rename(columns={"CODIGO": "COD_PRODUTO"})
        .groupby(["COD_PRODUTO", "PRODUTO"], dropna=False)
        .agg(
            QUANTIDADE_SOLICITADA=("QUANTIDADE_NUM", "sum"),
            DATA_HORA_DT=("DATA_HORA_DT", "max"),
        )
        .reset_index()
    )
    if entradas.empty:
        return pd.DataFrame(columns=colunas)

    embaladas = (
        dados[
            dados["ACAO_NORM"].isin(["PARCIAL", "FIM"])
            & (dados["ACAO_ETAPA"] == "EMBALAGEM")
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .rename(columns={"CODIGO": "COD_PRODUTO"})
        .groupby(["COD_PRODUTO", "PRODUTO"], dropna=False)
        .agg(QUANTIDADE_EMBALADA=("QUANTIDADE_NUM", "sum"))
        .reset_index()
    )
    fila = entradas.merge(embaladas, on=["COD_PRODUTO", "PRODUTO"], how="left")
    fila["QUANTIDADE_EMBALADA"] = fila["QUANTIDADE_EMBALADA"].fillna(0)
    fila["QUANTIDADE_PENDENTE"] = (fila["QUANTIDADE_SOLICITADA"] - fila["QUANTIDADE_EMBALADA"]).clip(lower=0)
    fila = fila[fila["QUANTIDADE_PENDENTE"] > 0].copy()
    if fila.empty:
        return pd.DataFrame(columns=colunas)

    fila["CHAVE_PRODUTO"] = chave_produto(fila)
    controles = dados[
        dados["ACAO_NORM"].isin(["INICIO", "PAUSA", "FIM"])
        & (dados["ACAO_ETAPA"] == "EMBALAGEM")
        & dados["DATA_HORA_DT"].notna()
    ].rename(columns={"CODIGO": "COD_PRODUTO"}).copy()
    if not controles.empty:
        controles["CHAVE_PRODUTO"] = chave_produto(controles)
        ultima = (
            controles.sort_values("DATA_HORA_DT", kind="mergesort")
            .groupby("CHAVE_PRODUTO", dropna=False)["ACAO_NORM"]
            .last()
            .to_dict()
        )
        fila["ULTIMA_ACAO_EMBALAGEM"] = fila["CHAVE_PRODUTO"].map(ultima).fillna("")
        fila["EM_ANDAMENTO"] = fila["ULTIMA_ACAO_EMBALAGEM"] == "INICIO"
        fila["PAUSADA"] = fila["ULTIMA_ACAO_EMBALAGEM"] == "PAUSA"
    else:
        fila["EM_ANDAMENTO"] = False
        fila["PAUSADA"] = False

    fila["EM_ANDAMENTO"] = fila["EM_ANDAMENTO"].fillna(False).astype(bool)
    fila["PAUSADA"] = fila["PAUSADA"].fillna(False).astype(bool)
    return fila[colunas].sort_values(["DATA_HORA_DT", "PRODUTO"], ascending=[True, True])


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


def render_detalhes_item(item):
    st.markdown(
        f"""
        <div class="detail-grid">
            <div class="detail-box">
                <div class="detail-label">Codigo</div>
                <div class="detail-value">{escape(str(item.get("COD_PRODUTO", "")) or "Sem codigo")}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Produto</div>
                <div class="detail-value">{escape(str(item.get("PRODUTO", "")) or "-")}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Solicitado</div>
                <div class="detail-value">{escape(numero(item.get("QUANTIDADE_SOLICITADA", 0)))}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Pendente</div>
                <div class="detail-value">{escape(numero(item.get("QUANTIDADE_PENDENTE", 0)))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Informacoes da embalagem", width="large")
def modal_informacao(item):
    render_detalhes_item(item)


@st.dialog("Iniciar embalagem", width="large")
def modal_inicio_embalagem(item, usuarios):
    render_detalhes_item(item)
    if not usuarios:
        st.error("Nenhum usuario foi encontrado na aba Usuarios.")
        return

    ordem = montar_ordem_embalagem(item)
    chave = chave_css_texto(item["COD_PRODUTO"], item["PRODUTO"], "inicio")
    trava = f"embalagem_trava_{chave}"
    with st.form(f"form_{chave}"):
        usuario = st.selectbox("Usuario da embalagem", usuarios)
        confirmar = st.form_submit_button(
            "Lancamento em andamento..." if st.session_state.get(trava) else "Confirmar inicio",
            use_container_width=True,
            disabled=bool(st.session_state.get(trava, False)),
        )

    if confirmar:
        st.session_state[trava] = True
        try:
            lancar_inicio_embalagem(ordem, usuario=usuario)
        except Exception as exc:
            st.session_state.pop(trava, None)
            st.error(str(exc))
        else:
            st.session_state.pop(trava, None)
            st.rerun()


@st.dialog("Pausar embalagem", width="large")
def modal_pausa_embalagem(item, usuarios):
    render_detalhes_item(item)
    if not usuarios:
        st.error("Nenhum usuario foi encontrado na aba Usuarios.")
        return

    ordem = montar_ordem_embalagem(item)
    chave = chave_css_texto(item["COD_PRODUTO"], item["PRODUTO"], "pausa")
    trava = f"embalagem_trava_{chave}"
    with st.form(f"form_{chave}"):
        usuario = st.selectbox("Usuario da embalagem", usuarios)
        confirmar = st.form_submit_button(
            "Lancamento em andamento..." if st.session_state.get(trava) else "Confirmar pausa",
            use_container_width=True,
            disabled=bool(st.session_state.get(trava, False)),
        )

    if confirmar:
        st.session_state[trava] = True
        try:
            lancar_pausa_embalagem(ordem, usuario=usuario)
        except Exception as exc:
            st.session_state.pop(trava, None)
            st.error(str(exc))
        else:
            st.session_state.pop(trava, None)
            st.rerun()


@st.dialog("Concluir embalagem", width="large")
def modal_conclusao(item, usuarios):
    render_detalhes_item(item)
    if not bool(item.get("EM_ANDAMENTO", False)) or bool(item.get("PAUSADA", False)):
        st.error("Inicie a embalagem antes de concluir.")
        return

    ordem = montar_ordem_embalagem(item)
    chave = chave_css_texto(item["COD_PRODUTO"], item["PRODUTO"], "conclusao")
    trava = f"embalagem_trava_{chave}"
    with st.form(f"form_{chave}"):
        quantidade = st.number_input(
            "Quantidade embalada",
            min_value=1,
            max_value=max(1, inteiro(item["QUANTIDADE_PENDENTE"])),
            value=max(1, inteiro(item["QUANTIDADE_PENDENTE"])),
            step=1,
        )
        confirmar = st.form_submit_button(
            "Lancamento em andamento..." if st.session_state.get(trava) else "Confirmar embalagem",
            use_container_width=True,
            disabled=bool(st.session_state.get(trava, False)),
        )
    if confirmar:
        st.session_state[trava] = True
        try:
            lancar_conclusao_embalagem(ordem, quantidade)
        except Exception as exc:
            st.session_state.pop(trava, None)
            st.error(str(exc))
        else:
            st.session_state.pop(trava, None)
            st.success("Embalagem registrada no historico.")
            st.rerun()


def render_card_embalagem(item, usuarios):
    chave_css = chave_css_texto(item["COD_PRODUTO"], item["PRODUTO"])
    produto = str(item["PRODUTO"]) or "Produto sem descricao"
    codigo = str(item["COD_PRODUTO"]) or "Sem codigo"
    em_andamento = bool(item.get("EM_ANDAMENTO", False))
    pausada = bool(item.get("PAUSADA", False))
    status_fluxo = "Pausado" if pausada else "Em andamento" if em_andamento else "Aguardando inicio"
    ordem = montar_ordem_embalagem(item)

    with st.container(border=True, key=f"embalagem_{chave_css}"):
        col_info, col_qtd, col_acoes = st.columns([6.6, .85, 1.8], vertical_alignment="center")
        with col_info:
            st.markdown(
                f"""
                <div>
                    <div class="order-name" title="{escape(produto)}">{escape(produto)}</div>
                    <span class="order-meta">Cod. {escape(codigo)}</span>
                    <div class="order-badges">
                        <span class="order-badge">Solicitado {escape(numero(item["QUANTIDADE_SOLICITADA"]))}</span>
                        <span class="order-badge">Embalado {escape(numero(item["QUANTIDADE_EMBALADA"]))}</span>
                        <span class="order-badge">{escape(status_fluxo)}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_qtd:
            st.markdown(
                f"""
                <div>
                    <div class="order-number">{escape(numero(item["QUANTIDADE_PENDENTE"]))}</div>
                    <div class="order-label">pendente</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_acoes:
            acao_1, acao_2, acao_3, acao_4 = st.columns(4, gap="small")
            with acao_1:
                key = f"iniciar_{chave_css}"
                trava = f"embalagem_trava_{key}"
                aplicar_icone_botao(key, ICONES_BOTOES["inicio"])
                desabilitado = (em_andamento and not pausada) or bool(st.session_state.get(trava, False))
                texto = "Retomar" if pausada else "Iniciar"
                if st.button(texto, key=key, help="Registrar inicio/retomada da embalagem", disabled=desabilitado):
                    modal_inicio_embalagem(item, usuarios)
            with acao_2:
                key = f"pausar_{chave_css}"
                trava = f"embalagem_trava_{key}"
                aplicar_icone_botao(key, ICONES_BOTOES["pausa"])
                desabilitado = pausada or not em_andamento or bool(st.session_state.get(trava, False))
                if st.button("Pausar", key=key, help="Pausar contagem da embalagem", disabled=desabilitado):
                    modal_pausa_embalagem(item, usuarios)
            with acao_3:
                key = f"consulta_{chave_css}"
                aplicar_icone_botao(key, ICONES_BOTOES["consulta"])
                if st.button("Informacao", key=key, help="Consultar item"):
                    modal_informacao(item)
            with acao_4:
                key = f"concluir_{chave_css}"
                aplicar_icone_botao(key, ICONES_BOTOES["conclusao"])
                desabilitado = pausada or not em_andamento
                if st.button("Concluir", key=key, help="Concluir embalagem", disabled=desabilitado):
                    modal_conclusao(item, usuarios)


def opcoes_encaminhamento(ordens, historico):
    if ordens.empty or historico.empty or "ACAO" not in historico.columns:
        return pd.DataFrame()

    dados = historico.copy()
    dados["ACAO_NORM"] = dados["ACAO"].map(acao_base_historico)
    dados["ACAO_ETAPA"] = dados["ACAO"].map(acao_etapa_historico)
    dados["QUANTIDADE_NUM"] = pd.to_numeric(dados["QUANTIDADE_NUM"], errors="coerce").fillna(0)
    dados = dados.rename(columns={"CODIGO": "COD_PRODUTO", "TIPO": "ABA_ORIGEM"})
    chaves = ["COD_PRODUTO", "PRODUTO"]

    aprovadas = (
        dados[
            dados["ACAO_NORM"].isin(["APROVADO", "PARCIAL", "FIM"])
            & (dados["ACAO_ETAPA"] == "QUALIDADE")
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .groupby(chaves, dropna=False)["QUANTIDADE_NUM"]
        .sum()
        .rename("QUANTIDADE_APROVADA")
        .reset_index()
    )
    if aprovadas.empty:
        return pd.DataFrame()

    entradas = (
        dados[
            (dados["ACAO_NORM"] == "ENTRADA")
            & (dados["ACAO_ETAPA"] == "EMBALAGEM")
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .groupby(chaves, dropna=False)["QUANTIDADE_NUM"]
        .sum()
        .rename("QUANTIDADE_ENVIADA_EMBALAGEM")
        .reset_index()
    )
    base = aprovadas.merge(entradas, on=chaves, how="left")
    base["QUANTIDADE_ENVIADA_EMBALAGEM"] = base["QUANTIDADE_ENVIADA_EMBALAGEM"].fillna(0)
    base["QUANTIDADE_DISPONIVEL"] = (
        base["QUANTIDADE_APROVADA"] - base["QUANTIDADE_ENVIADA_EMBALAGEM"]
    ).clip(lower=0)
    base = base[base["QUANTIDADE_DISPONIVEL"] > 0].copy()
    if base.empty:
        return base

    base["ABA_ORIGEM"] = "Embalagem"
    base["OP"] = ""
    base["USUARIO_RESPONSAVEL"] = ""
    base["ROTULO_EMBALAGEM"] = base.apply(
        lambda linha: f"{linha['COD_PRODUTO']} | {str(linha['PRODUTO'])[:100]}",
        axis=1,
    )
    return base.sort_values(["COD_PRODUTO", "PRODUTO"])


def render_puxar_ordem_embalagem(ordens, historico):
    opcoes = opcoes_encaminhamento(ordens, historico)
    if opcoes.empty:
        return
    with st.expander("Puxar item para embalagem"):
        rotulos = opcoes["ROTULO_EMBALAGEM"].tolist()
        selecionado = st.selectbox("Ordem/item", rotulos, key="puxar_embalagem_ordem")
        ordem = opcoes[opcoes["ROTULO_EMBALAGEM"] == selecionado].iloc[0]
        quantidade_key = "puxar_embalagem_quantidade_" + chave_css_texto(
            ordem["ABA_ORIGEM"],
            ordem["OP"],
            ordem["COD_PRODUTO"],
            ordem["PRODUTO"],
            ordem["USUARIO_RESPONSAVEL"],
        )
        with st.form("form_puxar_embalagem"):
            maximo = max(1, inteiro(ordem["QUANTIDADE_DISPONIVEL"]))
            quantidade = st.number_input(
                "Quantidade",
                min_value=1,
                max_value=maximo,
                value=maximo,
                step=1,
                key=quantidade_key,
            )
            confirmar = st.form_submit_button("Enviar para embalagem", use_container_width=True)
        if confirmar:
            try:
                lancar_encaminhamento_embalagem(ordem, quantidade)
            except Exception as exc:
                st.error(str(exc))
            else:
                st.success("Item enviado para embalagem.")
                st.rerun()


aplicar_estilo()
render_sidebar()

logo_branco = base64.b64encode(Path("Logo Branco.bmp").read_bytes()).decode("utf-8")
logo_goper = base64.b64encode(Path("logo preto goper.png").read_bytes()).decode("utf-8")

st.markdown(
    f"""
    <div class="page-head">
        <div>
            <h1>Embalagens</h1>
            <p>Itens aprovados e aguardando registro de embalagem.</p>
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
    usuarios = carregar_usuarios()
    ordens = carregar_ordens()
    historico = carregar_historico()
except Exception as exc:
    st.error("Nao foi possivel carregar os dados de embalagem.")
    st.caption(str(exc))
    st.stop()

operadores = usuarios_embalagem(usuarios)
fila = montar_fila_embalagem(historico)

f1, f2 = st.columns([5.6, 1], vertical_alignment="bottom")
with f1:
    if not operadores:
        st.warning("Nenhum usuario foi encontrado na aba Usuarios.")
with f2:
    if st.button("Atualizar", key="embalagem_atualizar", use_container_width=True):
        carregar_usuarios.clear()
        carregar_ordens.clear()
        carregar_historico.clear()
        st.rerun()

k1, k2, k3 = st.columns(3)
with k1:
    render_kpi("Itens na embalagem", len(fila), "Produtos aguardando embalagem")
with k2:
    render_kpi("Qtd. pendente", numero(fila["QUANTIDADE_PENDENTE"].sum() if not fila.empty else 0), "Total a embalar")
with k3:
    render_kpi("Qtd. embalada", numero(fila["QUANTIDADE_EMBALADA"].sum() if not fila.empty else 0), "Total registrado no periodo")

st.markdown('<div class="panel-title">Pendencias de embalagem</div>', unsafe_allow_html=True)
render_puxar_ordem_embalagem(ordens, historico)
if fila.empty:
    st.markdown('<div class="obs-box"><div class="obs-value">Nenhum item pendente para embalagem.</div></div>', unsafe_allow_html=True)
else:
    for _, linha in fila.iterrows():
        render_card_embalagem(linha, operadores)
