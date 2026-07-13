import pandas as pd
import streamlit as st

from utils.display_mode import ativar_modo_exibicao, page_link_icon, render_menu_lateral
from utils.sheets import (
    ABAS_PLANEJAMENTO,
    carregar_bd_produtos,
    carregar_ordens,
    carregar_usuarios,
    criar_ordem_planejamento,
    _normalizar,
)


st.set_page_config(
    page_title="Criar OP",
    page_icon="icones/menu.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("criar_op")
render_menu_lateral()


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
            max-width: 1240px;
            padding-top: 2.35rem;
            padding-bottom: .7rem;
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
            border-radius: 0;
            padding: 0;
            max-height: 42px;
            width: auto;
        }

        .page-head {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: .3cm;
            margin: 0 0 8px 0;
        }

        .page-head h1 {
            margin: 0;
            color: #000000;
            font-size: 26px;
            line-height: 1.1;
            font-weight: 900;
        }

        .page-head p {
            margin: 4px 0 0 0;
            color: #333333;
            font-size: 12px;
            line-height: 1.35;
        }

        div[data-testid="stMarkdownContainer"] p {
            margin-bottom: 0.25rem;
        }

        .op-top-card {
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 9px 12px;
            background: #ffffff;
            min-height: 44px;
            margin-top: 20px;
        }

        .op-top-label {
            color: #333333;
            font-size: 11px;
            font-weight: 800;
            margin-bottom: 2px;
        }

        .op-top-value {
            color: #000000;
            font-size: 16px;
            font-weight: 900;
            line-height: 1.15;
        }

        .op-work-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #000000;
            padding-bottom: 8px;
            margin-bottom: 10px;
        }

        .op-work-title strong {
            color: #000000;
            font-size: 15px;
            font-weight: 900;
        }

        .op-work-title span {
            color: #333333;
            font-size: 12px;
            font-weight: 800;
        }

        .op-subtitle {
            color: #000000;
            font-size: 13px;
            font-weight: 900;
            margin: 0 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid #000000;
        }

        .op-side-note {
            color: #333333;
            font-size: 11px;
            font-weight: 700;
            line-height: 1.3;
            margin: -2px 0 6px 0;
        }

        .op-section-title {
            border-bottom: 2px solid #000000;
            padding: 0 0 8px 0;
            margin: 0 0 10px 0;
            color: #000000;
            font-size: 14px;
            font-weight: 900;
        }

        .op-hint {
            color: #333333;
            font-size: 12px;
            font-weight: 750;
            min-height: 18px;
            margin: -2px 0 4px 0;
        }

        .op-suggestion-box {
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 10px;
            background: #fafafa;
            min-height: 100%;
        }

        .op-suggestion-title {
            font-size: 13px;
            font-weight: 900;
            margin-bottom: 8px;
            color: #000000;
        }

        .op-suggestion-row {
            display: grid;
            grid-template-columns: 68px 1fr 52px;
            gap: 8px;
            align-items: center;
            border-top: 1px solid #d8d8d8;
            padding: 6px 0;
            font-size: 12px;
            color: #000000;
        }

        .op-suggestion-row:first-of-type {
            border-top: 0;
        }

        .op-suggestion-row strong {
            font-size: 12px;
        }

        .op-suggestion-row span {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        div[data-testid="stTextInput"] div[data-baseweb="input"],
        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stDateInput"] div[data-baseweb="input"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-testid="stTextArea"] textarea {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            min-height: 40px !important;
            background: #ffffff !important;
        }

        div[data-testid="stTextInput"] *,
        div[data-testid="stNumberInput"] *,
        div[data-testid="stDateInput"] *,
        div[data-testid="stSelectbox"] * {
            background-color: #ffffff !important;
        }

        div[data-testid="stTextInput"],
        div[data-testid="stNumberInput"],
        div[data-testid="stDateInput"],
        div[data-testid="stSelectbox"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
        }

        div[data-testid="stTextInput"] > div,
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stDateInput"] > div,
        div[data-testid="stSelectbox"] > div {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
            min-height: 40px !important;
            overflow: hidden !important;
        }

        div[data-testid="stNumberInput"] > div {
            overflow: visible !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="input"],
        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stDateInput"] div[data-baseweb="input"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border: 0 !important;
            background: #ffffff !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="input"] *,
        div[data-testid="stNumberInput"] div[data-baseweb="input"] *,
        div[data-testid="stDateInput"] div[data-baseweb="input"] *,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stSelectbox"] div[role="combobox"] *,
        div[data-testid="stNumberInput"] > div *,
        div[data-testid="stDateInput"] > div *,
        div[data-testid="stTextInput"] > div *,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextArea"] textarea * {
            background: #ffffff !important;
            background-color: #ffffff !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {
            border: 0 !important;
            box-shadow: none !important;
            outline: none !important;
            background: #ffffff !important;
            background-color: #ffffff !important;
            min-height: 36px !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        div[data-testid="stTextInput"] input:disabled,
        div[data-testid="stTextInput"] input[disabled],
        div[data-testid="stTextInput"] div[data-baseweb="input"]:has(input:disabled),
        div[data-testid="stTextInput"] div[data-baseweb="input"]:has(input[disabled]) {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextInput"]:has(input:disabled),
        div[data-testid="stTextInput"]:has(input[disabled]),
        div[data-testid="stTextInput"]:has(input:disabled) *,
        div[data-testid="stTextInput"]:has(input[disabled]) * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stNumberInput"] input::placeholder,
        div[data-testid="stDateInput"] input::placeholder {
            background: #ffffff !important;
            color: #6b7280 !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextInput"],
        div[data-testid="stNumberInput"],
        div[data-testid="stDateInput"],
        div[data-testid="stSelectbox"] {
            margin-bottom: 12px !important;
        }

        div[data-testid="stNumberInput"] button {
            border: 2px solid #000000 !important;
            border-radius: 6px !important;
            min-height: 40px !important;
            width: 34px !important;
            background: #ffffff !important;
            margin-left: 3px !important;
            flex: 0 0 34px !important;
        }

        button {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            color: #000000 !important;
            background: #ffffff !important;
            font-weight: 800 !important;
        }

        label, [data-testid="stWidgetLabel"] p {
            font-size: 11px !important;
            font-weight: 800 !important;
            margin-bottom: 8px !important;
            line-height: 1.2 !important;
        }

        [data-testid="stAlert"] {
            padding: 6px 10px !important;
            margin: 4px 0 !important;
        }

        div[data-testid="column"] {
            gap: .7rem !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: .65rem !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff !important;
        }

        .st-key-criar_ordem_submit button {
            min-height: 40px !important;
            font-size: 13px !important;
            background: #ffffff !important;
        }

        .st-key-criar_ordem_submit {
            margin-top: 10px !important;
        }

        .st-key-criar_op_sugestao div[data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 118px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        st.image("icones/Logo Branco.bmp", width=72)
        st.image("icones/logo preto goper.png", width=32)
        st.markdown("</div>", unsafe_allow_html=True)
        page_link_icon("app.py", "Inicio", "icones/logo preto goper.png")
        page_link_icon("pages/Criar_OP.py", "Criar OP", "icones/producao.png")
        page_link_icon("pages/Producao.py", "Producao", "icones/producao.png")
        page_link_icon("pages/Qualidade.py", "Qualidade", "icones/qualidade.png")
        page_link_icon("pages/Embalagens.py", "Embalagens", "icones/embalagem.png")
        page_link_icon("pages/Historico_OP.py", "Historico OP", "icones/historico.png")
        page_link_icon("pages/Dashboard.py", "Dashboard", "icones/indicadores.png")


def numero(valor):
    valor = float(valor or 0)
    if valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")


def sugestoes_itens(ordens):
    if ordens.empty:
        return pd.DataFrame(columns=["COD_PRODUTO", "PRODUTO", "Ordens"])
    dados = ordens.copy()
    dados = dados[
        dados["COD_PRODUTO"].astype(str).str.strip().ne("")
        & dados["PRODUTO"].astype(str).str.strip().ne("")
    ].copy()
    if dados.empty:
        return pd.DataFrame(columns=["COD_PRODUTO", "PRODUTO", "Ordens"])
    return (
        dados.groupby(["COD_PRODUTO", "PRODUTO"], as_index=False)
        .agg(Ordens=("OP", "count"))
        .sort_values(["Ordens", "PRODUTO"], ascending=[False, True])
        .head(8)
    )


def produto_por_codigo(produtos, codigo):
    codigo_norm = _normalizar(codigo)
    if produtos.empty or not codigo_norm:
        return None
    encontrados = produtos[produtos["COD_PRODUTO"].map(_normalizar) == codigo_norm]
    if encontrados.empty:
        return None
    return encontrados.iloc[0].to_dict()


def nomes_usuarios(usuarios):
    if usuarios.empty or "Nome" not in usuarios.columns:
        return []
    return (
        usuarios["Nome"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda serie: serie.ne("")]
        .sort_values()
        .unique()
        .tolist()
    )


def proxima_op(ordens, aba):
    if ordens.empty or "ABA_ORIGEM" not in ordens.columns or "OP" not in ordens.columns:
        return "1"

    dados = ordens[ordens["ABA_ORIGEM"] == aba].copy()
    if dados.empty:
        return "1"

    numeros = []
    for valor in dados["OP"].dropna().astype(str):
        texto = valor.strip()
        if not texto.isdigit():
            continue
        if len(texto) > 1 and texto.startswith("0"):
            continue
        numeros.append(int(texto))

    if not numeros:
        return "1"
    return str(max(numeros) + 1)


def aplicar_sugestao(codigo):
    st.session_state["criar_op_codigo_pendente"] = str(codigo)
    st.rerun()


def rotulo_sugestao(item):
    return f"{item['COD_PRODUTO']} | {str(item['PRODUTO'])[:80]} | {numero(item['Ordens'])} ordem(ns)"


aplicar_estilo()
render_sidebar()

st.markdown(
    """
    <div class="page-head">
        <div>
            <h1>Criar OP</h1>
            <p>Cadastro direto no planejamento, mantendo blocos semanais e linhas de separacao.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    produtos = carregar_bd_produtos()
    ordens = carregar_ordens()
    usuarios = carregar_usuarios()
except Exception as exc:
    st.error("Nao foi possivel carregar os dados da planilha.")
    st.caption(str(exc))
    st.stop()

codigo_pendente = st.session_state.pop("criar_op_codigo_pendente", None)
if codigo_pendente is not None:
    st.session_state["criar_op_codigo"] = str(codigo_pendente)

codigo_atual = st.session_state.get("criar_op_codigo", "")
produto_encontrado = produto_por_codigo(produtos, codigo_atual)
sugestoes = sugestoes_itens(ordens)

with st.container(border=True):
    st.markdown(
        """
        <div class="op-work-title">
            <strong>Cadastro da ordem</strong>
            <span>Preencha, confira o item e grave direto no planejamento</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    topo_setor, topo_op, topo_cadastro = st.columns([0.34, 0.33, 0.33], gap="medium")
    with topo_setor:
        aba = st.selectbox("Setor", ABAS_PLANEJAMENTO, key="criar_op_setor")
    op_sugerida = proxima_op(ordens, aba)
    with topo_op:
        st.markdown(
            f"""
            <div class="op-top-card">
                <div class="op-top-label">PROXIMA OP SUGERIDA</div>
                <div class="op-top-value">{op_sugerida}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with topo_cadastro:
        st.markdown(
            """
            <div class="op-top-card">
                <div class="op-top-label">CADASTRO</div>
                <div class="op-top-value">Planejamento semanal</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col_form, col_sugestoes = st.columns([0.70, 0.30], gap="medium")

    with col_form:
        st.markdown('<div class="op-subtitle">Dados principais</div>', unsafe_allow_html=True)
        linha1 = st.columns([0.16, 0.24, 0.28, 0.32])
        with linha1[0]:
            op = st.text_input("N da OP", value=op_sugerida)
        with linha1[1]:
            quantidade_texto = st.text_input("Quantidade", value="1")
        with linha1[2]:
            data_prevista = st.date_input("Data prevista", format="DD/MM/YYYY")
        with linha1[3]:
            usuarios_lista = [""] + nomes_usuarios(usuarios)
            responsavel = st.selectbox("Responsavel", usuarios_lista)

        linha2 = st.columns([0.25, 0.75])
        with linha2[0]:
            codigo = st.text_input("Codigo do item", key="criar_op_codigo")
        produto_encontrado = produto_por_codigo(produtos, codigo)
        produto_padrao = produto_encontrado["PRODUTO"] if produto_encontrado else ""
        with linha2[1]:
            produto = st.text_input(
                "Descricao do item",
                value=produto_padrao,
                disabled=bool(produto_encontrado),
            )

        if produto_encontrado:
            detalhes = []
            for campo in ["CATEGORIA", "MARCA", "GRUPO"]:
                valor = str(produto_encontrado.get(campo, "")).strip()
                if valor:
                    detalhes.append(f"{campo.title()}: {valor}")
            info_item = f"Item encontrado: {produto_encontrado['PRODUTO']}"
            if detalhes:
                info_item += " | " + " | ".join(detalhes)
            st.markdown(f'<div class="op-hint">{info_item}</div>', unsafe_allow_html=True)
        elif codigo:
            st.markdown(
                '<div class="op-hint">Codigo nao localizado no Bd_produtos. Preencha a descricao manualmente para cadastrar atividade extra.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="op-hint"></div>', unsafe_allow_html=True)

        linha3 = st.columns([0.25, 0.75])
        with linha3[0]:
            data_abertura = st.date_input("Data de abertura", format="DD/MM/YYYY")
        with linha3[1]:
            obs = st.text_input("Observacoes")

        cod_peca = ""
        peca = ""
        qtd_pecas = ""
        if aba == ABAS_PLANEJAMENTO[2]:
            st.markdown('<div class="op-section-title" style="margin-top:8px;">Pecas</div>', unsafe_allow_html=True)
            linha4 = st.columns([0.22, 0.56, 0.22])
            with linha4[0]:
                cod_peca = st.text_input("Codigo da peca")
            with linha4[1]:
                peca = st.text_input("Descricao da peca")
            with linha4[2]:
                qtd_pecas = st.number_input("Qtd. pecas", min_value=0, value=0, step=1)

    with col_sugestoes:
        with st.container(border=True, key="criar_op_sugestao"):
            st.markdown('<div class="op-suggestion-title">Itens mais usados</div>', unsafe_allow_html=True)
            st.markdown('<div class="op-side-note">Use a lista apenas como atalho. Ao escolher um item, o codigo e preenchido automaticamente.</div>', unsafe_allow_html=True)
            rotulos_sugestoes = [""] + [rotulo_sugestao(item) for _, item in sugestoes.iterrows()]
            sugestao = st.selectbox("Usar sugestao", rotulos_sugestoes, label_visibility="collapsed")
            if sugestao:
                codigo_sugerido = sugestao.split("|", 1)[0].strip()
                if codigo_sugerido != str(st.session_state.get("criar_op_codigo", "")).strip():
                    aplicar_sugestao(codigo_sugerido)
        confirmar = st.button("Criar ordem", use_container_width=True, key="criar_ordem_submit")

if confirmar:
    descricao_final = produto_encontrado["PRODUTO"] if produto_encontrado else produto
    erros = []
    try:
        quantidade = int(str(quantidade_texto).strip())
    except (TypeError, ValueError):
        quantidade = 0

    if not str(op).strip():
        erros.append("Informe o numero da OP.")
    if not str(codigo).strip():
        erros.append("Informe o codigo do item.")
    if not str(descricao_final).strip():
        erros.append("Informe a descricao do item.")
    if quantidade <= 0:
        erros.append("Informe uma quantidade maior que zero.")

    if erros:
        for erro in erros:
            st.error(erro)
    else:
        dados = {
            "OP": op,
            "COD_PRODUTO": codigo,
            "PRODUTO": descricao_final,
            "QUANTIDADE": quantidade,
            "OBS": obs,
            "DATA_ABERTURA": data_abertura,
            "DATA_PREVISTA": data_prevista,
            "DATA": data_abertura,
            "USUARIO_RESPONSAVEL": responsavel,
            "COD_PECA": cod_peca,
            "PECA": peca,
            "QTD_PECAS": qtd_pecas,
        }
        try:
            resultado = criar_ordem_planejamento(aba, dados)
        except Exception as exc:
            st.error("Nao foi possivel criar a ordem.")
            st.caption(str(exc))
        else:
            bloco = "em novo bloco semanal" if resultado["novo_bloco"] else "no bloco semanal existente"
            st.success(f"Ordem criada na aba {resultado['aba']}, linha {resultado['linha']}, {bloco}.")
