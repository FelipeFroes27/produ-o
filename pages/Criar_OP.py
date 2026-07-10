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
            max-width: 1480px;
            padding-top: .25rem;
            padding-bottom: .7rem;
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
            border-radius: 0;
            padding: 0;
            max-height: 24px;
            width: auto;
        }

        .page-head {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: .3cm;
            margin: 0 0 10px 0;
        }

        .page-head h1 {
            margin: 0;
            color: #000000;
            font-size: 24px;
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

        .erp-panel {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            overflow: hidden;
            margin-top: 8px;
        }

        .erp-section {
            border-bottom: 1px solid #000000;
            background: #f7f7f7;
            padding: 8px 10px;
            color: #000000;
            font-size: 13px;
            font-weight: 900;
        }

        .erp-row {
            border-bottom: 1px solid #d0d0d0;
            padding: 6px 8px;
            background: #ffffff;
        }

        .erp-row:last-child {
            border-bottom: 0;
        }

        .erp-label {
            min-height: 38px;
            display: flex;
            align-items: center;
            color: #000000;
            font-size: 12px;
            font-weight: 900;
        }

        .erp-note {
            color: #333333;
            font-size: 12px;
            font-weight: 750;
            padding: 0 10px 6px 10px;
        }

        .erp-action {
            display: flex;
            justify-content: flex-end;
            padding-top: 4px;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        textarea,
        div[data-testid="stDateInput"] input,
        div[data-testid="stNumberInput"] input {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            min-height: 38px !important;
        }

        button {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            color: #000000 !important;
            background: #ffffff !important;
            font-weight: 800 !important;
        }

        label, [data-testid="stWidgetLabel"] p {
            font-size: 12px !important;
            font-weight: 800 !important;
            margin-bottom: 2px !important;
        }

        [data-testid="stAlert"] {
            padding: 6px 10px !important;
            margin: 4px 0 !important;
        }

        div[data-testid="column"] {
            gap: .25rem !important;
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
        page_link_icon("app.py", "Inicio", "icones/menu.png")
        page_link_icon("pages/Criar_OP.py", "Criar OP", "icones/menu.png")
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
    st.session_state["criar_op_codigo"] = str(codigo)
    st.rerun()


def rotulo_sugestao(item):
    return f"{item['COD_PRODUTO']} | {str(item['PRODUTO'])[:80]} | {numero(item['Ordens'])} ordem(ns)"


def linha_inicio(rotulo):
    st.markdown('<div class="erp-row">', unsafe_allow_html=True)
    col_label, col_campo = st.columns([0.18, 0.82], vertical_alignment="center")
    with col_label:
        st.markdown(f'<div class="erp-label">{rotulo}</div>', unsafe_allow_html=True)
    return col_campo


def linha_fim():
    st.markdown("</div>", unsafe_allow_html=True)


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

codigo_atual = st.session_state.get("criar_op_codigo", "")
produto_encontrado = produto_por_codigo(produtos, codigo_atual)
sugestoes = sugestoes_itens(ordens)

st.markdown('<div class="erp-panel">', unsafe_allow_html=True)
st.markdown('<div class="erp-section">Dados da ordem</div>', unsafe_allow_html=True)

with linha_inicio("Setor"):
    col_a, col_b = st.columns([0.32, 0.68])
    with col_a:
        aba = st.selectbox("Setor", ABAS_PLANEJAMENTO, key="criar_op_setor", label_visibility="collapsed")
    with col_b:
        rotulos_sugestoes = [""] + [rotulo_sugestao(item) for _, item in sugestoes.iterrows()]
        sugestao = st.selectbox("Atalho por itens frequentes", rotulos_sugestoes, label_visibility="collapsed")
linha_fim()

if sugestao:
    codigo_sugerido = sugestao.split("|", 1)[0].strip()
    if codigo_sugerido != str(st.session_state.get("criar_op_codigo", "")).strip():
        aplicar_sugestao(codigo_sugerido)

op_sugerida = proxima_op(ordens, aba)

with linha_inicio("N da OP"):
    col_a, col_b, col_c = st.columns([0.28, 0.28, 0.44])
    with col_a:
        op = st.text_input("N da OP", value=op_sugerida, label_visibility="collapsed")
    with col_b:
        quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1, label_visibility="collapsed")
    with col_c:
        usuarios_lista = [""] + nomes_usuarios(usuarios)
        responsavel = st.selectbox("Responsavel", usuarios_lista, label_visibility="collapsed")
linha_fim()

with linha_inicio("Codigo"):
    col_a, col_b = st.columns([0.25, 0.75])
    with col_a:
        codigo = st.text_input("Codigo do item", key="criar_op_codigo", label_visibility="collapsed")
    produto_encontrado = produto_por_codigo(produtos, codigo)
    produto_padrao = produto_encontrado["PRODUTO"] if produto_encontrado else ""
    with col_b:
        produto = st.text_input(
            "Descricao do item",
            value=produto_padrao,
            disabled=bool(produto_encontrado),
            label_visibility="collapsed",
        )
linha_fim()

if produto_encontrado:
    detalhes = []
    for campo in ["CATEGORIA", "MARCA", "GRUPO"]:
        valor = str(produto_encontrado.get(campo, "")).strip()
        if valor:
            detalhes.append(f"{campo.title()}: {valor}")
    info_item = f"Item encontrado: {produto_encontrado['PRODUTO']}"
    if detalhes:
        info_item += " | " + " | ".join(detalhes)
    st.markdown(f'<div class="erp-note">{info_item}</div>', unsafe_allow_html=True)
elif codigo:
    st.warning("Codigo nao encontrado no Bd_produtos. Confira o codigo ou preencha a descricao manualmente.")
else:
    st.markdown(f'<div class="erp-note">Proxima OP sugerida para {aba}: {op_sugerida}</div>', unsafe_allow_html=True)

with linha_inicio("Datas"):
    col_a, col_b, col_c = st.columns([0.25, 0.25, 0.5])
    with col_a:
        data_abertura = st.date_input("Data de abertura", label_visibility="collapsed")
    with col_b:
        data_prevista = st.date_input("Data prevista", label_visibility="collapsed")
    with col_c:
        obs = st.text_input("Observacoes", label_visibility="collapsed")
linha_fim()

cod_peca = ""
peca = ""
qtd_pecas = ""
if aba == ABAS_PLANEJAMENTO[2]:
    st.markdown('<div class="erp-section">Pecas</div>', unsafe_allow_html=True)
    with linha_inicio("Peca"):
        col_a, col_b, col_c = st.columns([0.25, 0.55, 0.2])
        with col_a:
            cod_peca = st.text_input("Codigo da peca", label_visibility="collapsed")
        with col_b:
            peca = st.text_input("Descricao da peca", label_visibility="collapsed")
        with col_c:
            qtd_pecas = st.number_input("Qtd. pecas", min_value=0, value=0, step=1, label_visibility="collapsed")
    linha_fim()

st.markdown("</div>", unsafe_allow_html=True)
acao_col1, acao_col2 = st.columns([0.82, 0.18])
with acao_col2:
    confirmar = st.button("Criar ordem", use_container_width=True)

if confirmar:
    descricao_final = produto_encontrado["PRODUTO"] if produto_encontrado else produto
    erros = []
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
