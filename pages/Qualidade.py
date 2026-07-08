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
    lancar_aprovacao_qualidade,
    lancar_encaminhamento_qualidade,
    lancar_inicio_qualidade,
    lancar_pausa_qualidade,
    lancar_reprovacao_qualidade,
)


st.set_page_config(
    page_title="Qualidade",
    page_icon="icones/consulta-logo-refinado.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("qualidade")
render_menu_lateral()

ICONES_BOTOES = {
    "inicio": "start-up.png",
    "pausa": "pausa.png",
    "aprovacao": "verificado.png",
    "consulta": "informacoes.png",
    "reprovacao": "reprovar.png",
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

        .quality-card {
            padding: 2px 0;
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
        .obs-box,
        .completion-box {
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

        .completion-spacer {
            height: 28px;
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
        st.page_link("pages/Historico_OP.py", label="Histórico OP")
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
    return chave.strip("_") or "qualidade"


def chave_qualidade(df, colunas):
    return df[colunas].fillna("").astype(str).apply(
        lambda linha: "|".join(chave_texto(valor) for valor in linha),
        axis=1,
    )


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


def usuarios_qualidade(usuarios):
    if usuarios.empty or "Cargo" not in usuarios.columns:
        return []
    cargo = usuarios["Cargo"].fillna("").astype(str).str.upper()
    return sorted(
        usuarios.loc[cargo.str.contains("QUALIDADE", na=False), "Nome"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda serie: serie.ne("")]
        .unique()
        .tolist()
    )


def montar_fila_qualidade(historico, ordens):
    colunas_saida = [
        "USUARIO_RESPONSAVEL",
        "OP",
        "COD_PRODUTO",
        "PRODUTO",
        "ABA_ORIGEM",
        "QUANTIDADE_PENDENTE",
        "QUANTIDADE_SOLICITADA",
        "QUANTIDADE_AVALIADA",
        "DATA_HORA_DT",
        "STATUS",
        "REALIZADO_NUM",
        "SALDO_NUM",
        "LINHA_PLANILHA",
        "OBS",
        "DATA_PRIORIDADE",
        "ATRASADA",
        "DIAS_ATRASO",
        "TEM_ORDEM",
        "EM_ANDAMENTO",
        "PAUSADA",
    ]
    if historico.empty or "ACAO" not in historico.columns:
        return pd.DataFrame(columns=colunas_saida)

    dados = historico.copy()
    dados["ACAO_NORM"] = dados["ACAO"].map(acao_base_historico)
    dados["ACAO_ETAPA"] = dados["ACAO"].map(acao_etapa_historico)
    dados["QUANTIDADE_NUM"] = pd.to_numeric(dados["QUANTIDADE_NUM"], errors="coerce").fillna(0)
    chaves_historico = ["USUARIO_RESPONSAVEL", "OP", "CODIGO", "PRODUTO", "TIPO"]

    solicitacoes = (
        dados[
            (dados["ACAO_NORM"] == "ENTRADA")
            & (dados["ACAO_ETAPA"] == "QUALIDADE")
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .groupby(chaves_historico, dropna=False)
        .agg(
            QUANTIDADE_SOLICITADA=("QUANTIDADE_NUM", "sum"),
            DATA_HORA_DT=("DATA_HORA_DT", "max"),
        )
        .reset_index()
    )
    if solicitacoes.empty:
        return pd.DataFrame(columns=colunas_saida)

    avaliacoes = (
        dados[
            (
                dados["ACAO_NORM"].isin(["APROVADO", "REPROVADO", "PARCIAL", "FIM"])
                & (dados["ACAO_ETAPA"] == "QUALIDADE")
            )
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .groupby(chaves_historico, dropna=False)
        .agg(QUANTIDADE_AVALIADA=("QUANTIDADE_NUM", "sum"))
        .reset_index()
    )
    fila = solicitacoes.merge(avaliacoes, on=chaves_historico, how="left")
    fila["QUANTIDADE_AVALIADA"] = fila["QUANTIDADE_AVALIADA"].fillna(0)
    fila["QUANTIDADE_PENDENTE"] = (fila["QUANTIDADE_SOLICITADA"] - fila["QUANTIDADE_AVALIADA"]).clip(lower=0)
    fila = fila[fila["QUANTIDADE_PENDENTE"] > 0].copy()
    if fila.empty:
        return pd.DataFrame(columns=colunas_saida)

    fila = fila.rename(columns={"CODIGO": "COD_PRODUTO", "TIPO": "ABA_ORIGEM"})
    fila["CHAVE_QUALIDADE"] = chave_qualidade(
        fila,
        ["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"],
    )

    ordens_base = ordens.copy()
    if not ordens_base.empty:
        ordens_base["CHAVE_QUALIDADE"] = chave_qualidade(
            ordens_base,
            ["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"],
        )
        ordens_base = ordens_base.drop_duplicates("CHAVE_QUALIDADE", keep="first")
        extras = [
            "CHAVE_QUALIDADE",
            "STATUS",
            "REALIZADO_NUM",
            "SALDO_NUM",
            "LINHA_PLANILHA",
            "OBS",
            "DATA_PRIORIDADE",
            "ATRASADA",
            "DIAS_ATRASO",
        ]
        fila = fila.merge(ordens_base[[col for col in extras if col in ordens_base.columns]], on="CHAVE_QUALIDADE", how="left")

    if "LINHA_PLANILHA" in fila.columns:
        fila["TEM_ORDEM"] = fila["LINHA_PLANILHA"].notna()
    else:
        fila["TEM_ORDEM"] = False

    controles = dados[
        dados["ACAO_NORM"].isin(["INICIO", "PAUSA", "FIM"])
        & (dados["ACAO_ETAPA"] == "QUALIDADE")
        & dados["DATA_HORA_DT"].notna()
    ].copy()
    if not controles.empty:
        controles = controles.rename(columns={"CODIGO": "COD_PRODUTO", "TIPO": "ABA_ORIGEM"})
        controles["CHAVE_QUALIDADE"] = chave_qualidade(
            controles,
            ["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"],
        )
        ultima = (
            controles.sort_values("DATA_HORA_DT")
            .groupby("CHAVE_QUALIDADE", dropna=False)["ACAO_NORM"]
            .last()
            .to_dict()
        )
        fila["ULTIMA_ACAO_QUALIDADE"] = fila["CHAVE_QUALIDADE"].map(ultima).fillna("")
        fila["EM_ANDAMENTO"] = fila["ULTIMA_ACAO_QUALIDADE"] == "INICIO"
        fila["PAUSADA"] = fila["ULTIMA_ACAO_QUALIDADE"] == "PAUSA"
    else:
        fila["EM_ANDAMENTO"] = False
        fila["PAUSADA"] = False
    for coluna in colunas_saida:
        if coluna not in fila.columns:
            fila[coluna] = "" if coluna not in ["REALIZADO_NUM", "SALDO_NUM", "DIAS_ATRASO"] else 0
    fila["REALIZADO_NUM"] = pd.to_numeric(fila["REALIZADO_NUM"], errors="coerce").fillna(0)
    fila["SALDO_NUM"] = pd.to_numeric(fila["SALDO_NUM"], errors="coerce").fillna(0)
    fila["ATRASADA"] = fila["ATRASADA"].fillna(False).astype(bool)
    fila["EM_ANDAMENTO"] = fila["EM_ANDAMENTO"].fillna(False).astype(bool)
    fila["PAUSADA"] = fila["PAUSADA"].fillna(False).astype(bool)
    return fila[colunas_saida].sort_values(["DATA_HORA_DT", "OP"], ascending=[True, True])


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


def resumo_prazo(linha):
    data = linha.get("DATA_PRIORIDADE")
    if pd.isna(data) or str(data).strip() == "":
        return ""
    data = pd.to_datetime(data, errors="coerce")
    if pd.isna(data):
        return ""
    if bool(linha.get("ATRASADA", False)):
        return f"Atrasada ha {int(float(linha.get('DIAS_ATRASO', 0) or 0))} dia(s)"
    if data.date() == pd.Timestamp.today().date():
        return "Para hoje"
    return f"Prazo {data.strftime('%d/%m/%Y')}"


def render_detalhes_ordem(ordem):
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
                <div class="detail-label">Responsavel</div>
                <div class="detail-value">{escape(str(ordem["USUARIO_RESPONSAVEL"]) or "-")}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Produto</div>
                <div class="detail-value">{escape(str(ordem["PRODUTO"]) or "-")}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Pendente qualidade</div>
                <div class="detail-value">{escape(numero(ordem["QUANTIDADE_PENDENTE"]))}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Realizado atual</div>
                <div class="detail-value">{escape(numero(ordem["REALIZADO_NUM"]))}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">Status</div>
                <div class="detail-value">{escape(str(ordem.get("STATUS", "-")) or "-")}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    observacao = str(ordem.get("OBS", "")).strip() or "-"
    st.markdown(
        f"""
        <div class="obs-box">
            <div class="obs-label">Observacoes</div>
            <div class="obs-value">{escape(observacao)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Informacoes da ordem", width="large")
def modal_informacao(ordem):
    render_detalhes_ordem(ordem)


@st.dialog("Iniciar qualidade", width="large")
def modal_inicio_qualidade(ordem, avaliadores):
    render_detalhes_ordem(ordem)
    if not avaliadores:
        st.error("Nenhum usuario com cargo Qualidade foi encontrado.")
        return

    chave = f"{ordem['ABA_ORIGEM']}_{ordem['OP']}_{ordem['COD_PRODUTO']}_inicio"
    trava = f"qualidade_trava_{chave}"
    with st.form(f"form_{chave}"):
        usuario = st.selectbox("Usuario da qualidade", avaliadores)
        confirmar = st.form_submit_button(
            "Lancamento em andamento..." if st.session_state.get(trava) else "Confirmar inicio",
            use_container_width=True,
            disabled=bool(st.session_state.get(trava, False)),
        )

    if confirmar:
        st.session_state[trava] = True
        try:
            lancar_inicio_qualidade(ordem, usuario)
        except Exception as exc:
            st.session_state.pop(trava, None)
            st.error(str(exc))
        else:
            st.session_state.pop(trava, None)
            st.rerun()


@st.dialog("Pausar qualidade", width="large")
def modal_pausa_qualidade(ordem, avaliadores):
    render_detalhes_ordem(ordem)
    if not avaliadores:
        st.error("Nenhum usuario com cargo Qualidade foi encontrado.")
        return

    chave = f"{ordem['ABA_ORIGEM']}_{ordem['OP']}_{ordem['COD_PRODUTO']}_pausa"
    trava = f"qualidade_trava_{chave}"
    with st.form(f"form_{chave}"):
        usuario = st.selectbox("Usuario da qualidade", avaliadores)
        confirmar = st.form_submit_button(
            "Lancamento em andamento..." if st.session_state.get(trava) else "Confirmar pausa",
            use_container_width=True,
            disabled=bool(st.session_state.get(trava, False)),
        )

    if confirmar:
        st.session_state[trava] = True
        try:
            lancar_pausa_qualidade(ordem, usuario)
        except Exception as exc:
            st.session_state.pop(trava, None)
            st.error(str(exc))
        else:
            st.session_state.pop(trava, None)
            st.rerun()


@st.dialog("Aprovar qualidade", width="large")
def modal_aprovacao(ordem, avaliadores, usuario_padrao=""):
    render_detalhes_ordem(ordem)
    if not avaliadores:
        st.error("Nenhum usuario com cargo Qualidade foi encontrado.")
        return

    chave = f"{ordem['ABA_ORIGEM']}_{ordem['OP']}_{ordem['COD_PRODUTO']}_aprovacao"
    trava = f"qualidade_trava_{chave}"
    with st.form(f"form_{chave}"):
        indice_usuario = avaliadores.index(usuario_padrao) if usuario_padrao in avaliadores else 0
        usuario = st.selectbox("Usuario da qualidade", avaliadores, index=indice_usuario)
        quantidade = st.number_input(
            "Quantidade aprovada",
            min_value=1,
            max_value=max(1, inteiro(ordem["QUANTIDADE_PENDENTE"])),
            value=max(1, inteiro(ordem["QUANTIDADE_PENDENTE"])),
            step=1,
        )
        enviar_embalagem = st.checkbox(
            "Enviar para embalagem",
            key=f"embalagem_{chave}",
            help="Encaminha a quantidade aprovada para a fila de embalagem.",
        )
        confirmar = st.form_submit_button(
            "Aprovacao em andamento..." if st.session_state.get(trava) else "Confirmar aprovacao",
            use_container_width=True,
            disabled=bool(st.session_state.get(trava, False)),
        )

    if confirmar:
        st.session_state[trava] = True
        try:
            lancar_aprovacao_qualidade(ordem, quantidade, usuario, embalagem=enviar_embalagem)
        except Exception as exc:
            st.session_state.pop(trava, None)
            st.error(str(exc))
        else:
            st.session_state.pop(trava, None)
            st.success("Aprovacao registrada no historico.")
            st.rerun()


@st.dialog("Reprovar qualidade", width="large")
def modal_reprovacao(ordem, avaliadores, usuario_padrao=""):
    render_detalhes_ordem(ordem)
    if not avaliadores:
        st.error("Nenhum usuario com cargo Qualidade foi encontrado.")
        return
    if not bool(ordem.get("TEM_ORDEM", False)):
        st.error("Nao foi possivel localizar a linha da ordem na programacao atual para subtrair o realizado.")
        return

    maximo = min(inteiro(ordem["QUANTIDADE_PENDENTE"]), inteiro(ordem["REALIZADO_NUM"]))
    if maximo <= 0:
        st.error("Esta ordem nao possui realizado suficiente para reprovar.")
        return

    chave = f"{ordem['ABA_ORIGEM']}_{ordem['OP']}_{ordem['COD_PRODUTO']}_reprovacao"
    trava = f"qualidade_trava_{chave}"
    with st.form(f"form_{chave}"):
        indice_usuario = avaliadores.index(usuario_padrao) if usuario_padrao in avaliadores else 0
        usuario = st.selectbox("Usuario da qualidade", avaliadores, index=indice_usuario)
        quantidade = st.number_input(
            "Quantidade reprovada",
            min_value=1,
            max_value=maximo,
            value=maximo,
            step=1,
        )
        confirmar = st.form_submit_button(
            "Reprovacao em andamento..." if st.session_state.get(trava) else "Confirmar reprovacao",
            use_container_width=True,
            disabled=bool(st.session_state.get(trava, False)),
        )

    if confirmar:
        st.session_state[trava] = True
        try:
            lancar_reprovacao_qualidade(ordem, quantidade, usuario)
        except Exception as exc:
            st.session_state.pop(trava, None)
            st.error(str(exc))
        else:
            st.session_state.pop(trava, None)
            st.success("Reprovacao registrada e realizado ajustado na ordem.")
            st.rerun()


def render_card_qualidade(linha, avaliadores):
    chave_css = chave_css_texto(linha["ABA_ORIGEM"], linha["OP"], linha["COD_PRODUTO"], linha["USUARIO_RESPONSAVEL"])
    produto = str(linha["PRODUTO"]) or "Produto sem descricao"
    op = str(linha["OP"]) or "Sem OP"
    codigo = str(linha["COD_PRODUTO"]) or "Sem codigo"
    em_andamento = bool(linha.get("EM_ANDAMENTO", False))
    pausada = bool(linha.get("PAUSADA", False))
    status_fluxo = "Pausado" if pausada else "Em andamento" if em_andamento else "Aguardando inicio"

    with st.container(border=True, key=f"qualidade_{chave_css}"):
        col_info, col_qtd, col_acoes = st.columns([6.25, .85, 2.2], vertical_alignment="center")
        with col_info:
            st.markdown(
                f"""
                <div class="quality-card">
                    <div class="order-name" title="{escape(produto)}">Ordem - {escape(op)} | {escape(produto)}</div>
                    <span class="order-meta">
                        {escape(str(linha["ABA_ORIGEM"]))} | Cod. {escape(codigo)} | Responsavel {escape(str(linha["USUARIO_RESPONSAVEL"]))} | {escape(resumo_prazo(linha))}
                    </span>
                    <div class="order-badges">
                        <span class="order-badge">Pendente qualidade {escape(numero(linha["QUANTIDADE_PENDENTE"]))}</span>
                        <span class="order-badge">Solicitado {escape(numero(linha["QUANTIDADE_SOLICITADA"]))}</span>
                        <span class="order-badge">Avaliado {escape(numero(linha["QUANTIDADE_AVALIADA"]))}</span>
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
                    <div class="order-number">{escape(numero(linha["QUANTIDADE_PENDENTE"]))}</div>
                    <div class="order-label">pendente</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_acoes:
            acao_1, acao_2, acao_3, acao_4, acao_5 = st.columns(5, gap="small")
            with acao_1:
                key = f"iniciar_{chave_css}"
                trava = f"qualidade_trava_{key}"
                aplicar_icone_botao(key, ICONES_BOTOES["inicio"])
                desabilitado = (em_andamento and not pausada) or bool(st.session_state.get(trava, False))
                texto = "Retomar" if pausada else "Iniciar"
                if st.button(texto, key=key, help="Registrar inicio/retomada da qualidade", disabled=desabilitado):
                    modal_inicio_qualidade(linha, avaliadores)
            with acao_2:
                key = f"pausar_{chave_css}"
                trava = f"qualidade_trava_{key}"
                aplicar_icone_botao(key, ICONES_BOTOES["pausa"])
                desabilitado = pausada or not em_andamento or bool(st.session_state.get(trava, False))
                if st.button("Pausar", key=key, help="Pausar contagem da qualidade", disabled=desabilitado):
                    modal_pausa_qualidade(linha, avaliadores)
            with acao_3:
                key = f"aprovar_{chave_css}"
                aplicar_icone_botao(key, ICONES_BOTOES["aprovacao"])
                desabilitado = pausada or not em_andamento
                if st.button("Aprovar", key=key, help="Aprovar quantidade na qualidade", disabled=desabilitado):
                    modal_aprovacao(linha, avaliadores)
            with acao_4:
                key = f"consulta_{chave_css}"
                aplicar_icone_botao(key, ICONES_BOTOES["consulta"])
                if st.button("Informacao", key=key, help="Consultar ordem"):
                    modal_informacao(linha)
            with acao_5:
                key = f"reprovar_{chave_css}"
                aplicar_icone_botao(key, ICONES_BOTOES["reprovacao"])
                desabilitado = pausada or not em_andamento
                if st.button("Reprovar", key=key, help="Reprovar quantidade na qualidade", disabled=desabilitado):
                    modal_reprovacao(linha, avaliadores)


def chave_fluxo(df):
    return df[["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"]].fillna("").astype(str).apply(
        lambda linha: "|".join(chave_texto(valor) for valor in linha),
        axis=1,
    )


def opcoes_encaminhamento(ordens, historico):
    if ordens.empty or historico.empty or "ACAO" not in historico.columns:
        return pd.DataFrame()

    dados = historico.copy()
    dados["ACAO_NORM"] = dados["ACAO"].map(acao_base_historico)
    dados["ACAO_ETAPA"] = dados["ACAO"].map(acao_etapa_historico)
    dados["QUANTIDADE_NUM"] = pd.to_numeric(dados["QUANTIDADE_NUM"], errors="coerce").fillna(0)
    dados = dados.rename(columns={"CODIGO": "COD_PRODUTO", "TIPO": "ABA_ORIGEM"})
    chaves = ["ABA_ORIGEM", "OP", "COD_PRODUTO", "PRODUTO", "USUARIO_RESPONSAVEL"]

    finalizadas = (
        dados[
            (dados["ACAO_NORM"] == "FIM")
            & dados["ACAO_ETAPA"].isin(["PRODUCAO", "MANUTENCAO", "PECAS"])
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .groupby(chaves, dropna=False)["QUANTIDADE_NUM"]
        .sum()
        .rename("QUANTIDADE_FINALIZADA")
        .reset_index()
    )
    if finalizadas.empty:
        return pd.DataFrame()

    entradas = (
        dados[
            (dados["ACAO_NORM"] == "ENTRADA")
            & (dados["ACAO_ETAPA"] == "QUALIDADE")
            & (dados["QUANTIDADE_NUM"] > 0)
        ]
        .groupby(chaves, dropna=False)["QUANTIDADE_NUM"]
        .sum()
        .rename("QUANTIDADE_ENVIADA_QUALIDADE")
        .reset_index()
    )
    base = finalizadas.merge(entradas, on=chaves, how="left")
    base["QUANTIDADE_ENVIADA_QUALIDADE"] = base["QUANTIDADE_ENVIADA_QUALIDADE"].fillna(0)
    base["QUANTIDADE_DISPONIVEL"] = (
        base["QUANTIDADE_FINALIZADA"] - base["QUANTIDADE_ENVIADA_QUALIDADE"]
    ).clip(lower=0)
    base = base[base["QUANTIDADE_DISPONIVEL"] > 0].copy()
    if base.empty:
        return base

    ordens_base = ordens.copy()
    ordens_base["CHAVE_FLUXO"] = chave_fluxo(ordens_base)
    base["CHAVE_FLUXO"] = chave_fluxo(base)
    base = base.merge(
        ordens_base.drop_duplicates("CHAVE_FLUXO", keep="first"),
        on="CHAVE_FLUXO",
        how="left",
        suffixes=("", "_ORDEM"),
    )
    for coluna in chaves:
        coluna_ordem = f"{coluna}_ORDEM"
        if coluna_ordem in base.columns:
            base[coluna] = base[coluna_ordem].where(base[coluna_ordem].fillna("").astype(str).str.strip().ne(""), base[coluna])
    base["ROTULO_QUALIDADE"] = base.apply(
        lambda linha: f"{linha['ABA_ORIGEM']} | OP {linha['OP']} | {linha['COD_PRODUTO']} | {str(linha['PRODUTO'])[:80]}",
        axis=1,
    )
    return base.sort_values(["ABA_ORIGEM", "OP", "COD_PRODUTO"])


def render_puxar_ordem_qualidade(ordens, historico):
    opcoes = opcoes_encaminhamento(ordens, historico)
    if opcoes.empty:
        return
    with st.expander("Puxar ordem para qualidade"):
        with st.form("form_puxar_qualidade"):
            rotulos = opcoes["ROTULO_QUALIDADE"].tolist()
            selecionado = st.selectbox("Ordem", rotulos)
            ordem = opcoes[opcoes["ROTULO_QUALIDADE"] == selecionado].iloc[0]
            maximo = max(1, inteiro(ordem["QUANTIDADE_DISPONIVEL"]))
            quantidade = st.number_input("Quantidade", min_value=1, max_value=maximo, value=maximo, step=1)
            confirmar = st.form_submit_button("Enviar para qualidade", use_container_width=True)
        if confirmar:
            try:
                lancar_encaminhamento_qualidade(ordem, quantidade)
            except Exception as exc:
                st.error(str(exc))
            else:
                st.success("Ordem enviada para qualidade.")
                st.rerun()


aplicar_estilo()
render_sidebar()

logo_branco = base64.b64encode(Path("Logo Branco.bmp").read_bytes()).decode("utf-8")
logo_goper = base64.b64encode(Path("logo preto goper.png").read_bytes()).decode("utf-8")

st.markdown(
    f"""
    <div class="page-head">
        <div>
            <h1>Qualidade</h1>
            <p>Ordens enviadas para aprovacao ou reprovacao da qualidade.</p>
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
    st.error("Nao foi possivel carregar os dados da qualidade.")
    st.caption(str(exc))
    st.stop()

avaliadores = usuarios_qualidade(usuarios)
fila = montar_fila_qualidade(historico, ordens)

f1, f2 = st.columns([5.6, 1], vertical_alignment="bottom")
with f1:
    if not avaliadores:
        st.warning("Nenhum usuario com cargo Qualidade foi encontrado na aba Usuarios.")
with f2:
    if st.button("Atualizar", key="qualidade_atualizar", use_container_width=True):
        carregar_usuarios.clear()
        carregar_ordens.clear()
        carregar_historico.clear()
        st.rerun()

k1, k2, k3 = st.columns(3)
with k1:
    render_kpi("Ordens na qualidade", len(fila), "Lancamentos aguardando avaliacao")
with k2:
    render_kpi("Qtd. pendente", numero(fila["QUANTIDADE_PENDENTE"].sum() if not fila.empty else 0), "Total aguardando qualidade")
with k3:
    sem_linha = int((~fila["TEM_ORDEM"]).sum()) if not fila.empty and "TEM_ORDEM" in fila.columns else 0
    render_kpi("Sem linha atual", sem_linha, "Pendencias sem ordem localizada")

st.markdown('<div class="panel-title">Pendencias da qualidade</div>', unsafe_allow_html=True)
render_puxar_ordem_qualidade(ordens, historico)
if fila.empty:
    st.markdown('<div class="obs-box"><div class="obs-value">Nenhuma ordem pendente para qualidade.</div></div>', unsafe_allow_html=True)
else:
    for _, linha in fila.iterrows():
        render_card_qualidade(linha, avaliadores)
