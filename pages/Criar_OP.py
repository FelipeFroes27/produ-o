from html import escape

import pandas as pd
import streamlit as st

from utils.display_mode import ativar_modo_exibicao, render_menu_lateral
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
    page_icon="icones/consulta-logo-refinado.png",
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
            margin: 0 0 .3cm 0;
        }

        .page-head h1 {
            margin: 0;
            color: #000000;
            font-size: 34px;
            line-height: 1.1;
            font-weight: 900;
        }

        .page-head p {
            margin: 8px 0 0 0;
            color: #333333;
            font-size: 14px;
            line-height: 1.35;
        }

        .suggestion-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .3cm;
            margin-bottom: .3cm;
        }

        .suggestion-card {
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 12px;
            min-height: 88px;
            background: #ffffff;
        }

        .suggestion-code {
            font-size: 12px;
            color: #333333;
            font-weight: 850;
        }

        .suggestion-name {
            margin-top: 6px;
            color: #000000;
            font-size: 14px;
            line-height: 1.2;
            font-weight: 850;
            overflow-wrap: anywhere;
        }

        .suggestion-count {
            margin-top: 7px;
            color: #333333;
            font-size: 12px;
            font-weight: 700;
        }

        div[data-testid="stForm"] {
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        textarea,
        div[data-testid="stDateInput"] input,
        div[data-testid="stNumberInput"] input {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        button {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            color: #000000 !important;
            background: #ffffff !important;
            font-weight: 800 !important;
        }

        @media (max-width: 1100px) {
            .suggestion-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
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
        st.page_link("pages/Criar_OP.py", label="Criar OP")
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


aplicar_estilo()
render_sidebar()

st.markdown(
    """
    <div class="page-head">
        <div>
            <h1>Criar OP</h1>
            <p>Cadastro de novas ordens diretamente no planejamento, mantendo blocos semanais e linhas de separacao.</p>
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

sugestoes = sugestoes_itens(ordens)
if not sugestoes.empty:
    st.markdown("**Sugestoes pelos itens mais usados**")
    cols = st.columns(4)
    for indice, item in sugestoes.iterrows():
        col = cols[int(indice) % 4]
        with col:
            st.markdown(
                f"""
                <div class="suggestion-card">
                    <div class="suggestion-code">Cod. {escape(str(item["COD_PRODUTO"]))}</div>
                    <div class="suggestion-name">{escape(str(item["PRODUTO"]))}</div>
                    <div class="suggestion-count">{escape(numero(item["Ordens"]))} ordem(ns)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Usar item", key=f"sugestao_{item['COD_PRODUTO']}_{indice}", use_container_width=True):
                aplicar_sugestao(item["COD_PRODUTO"])

codigo_atual = st.session_state.get("criar_op_codigo", "")
produto_encontrado = produto_por_codigo(produtos, codigo_atual)
aba = st.selectbox("Setor", ABAS_PLANEJAMENTO, key="criar_op_setor")
op_sugerida = proxima_op(ordens, aba)
st.caption(f"Proxima OP sugerida para {aba}: {op_sugerida}")

codigo = st.text_input("Codigo do item", key="criar_op_codigo")
produto_encontrado = produto_por_codigo(produtos, codigo)
if produto_encontrado:
    detalhes = []
    for campo in ["CATEGORIA", "MARCA", "GRUPO"]:
        valor = str(produto_encontrado.get(campo, "")).strip()
        if valor:
            detalhes.append(f"{campo.title()}: {valor}")
    st.success(f"Item encontrado: {produto_encontrado['PRODUTO']}")
    if detalhes:
        st.caption(" | ".join(detalhes))
elif codigo:
    st.warning("Codigo nao encontrado no Bd_produtos. Confira o codigo ou preencha a descricao manualmente.")

with st.form("form_criar_op"):
    st.markdown("**Dados da ordem**")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.text_input("Setor selecionado", value=aba, disabled=True)
    with col2:
        op = st.text_input("N da OP", value=op_sugerida)
    with col3:
        quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)

    produto_padrao = produto_encontrado["PRODUTO"] if produto_encontrado else ""
    produto = st.text_input(
        "Descricao do item",
        value=produto_padrao,
        disabled=bool(produto_encontrado),
    )

    col6, col7, col8 = st.columns([1, 1, 1])
    with col6:
        data_abertura = st.date_input("Data de abertura")
    with col7:
        data_prevista = st.date_input("Data prevista")
    with col8:
        usuarios_lista = [""] + nomes_usuarios(usuarios)
        responsavel = st.selectbox("Responsavel", usuarios_lista)

    obs = st.text_area("Observacoes", height=92)

    cod_peca = ""
    peca = ""
    qtd_pecas = ""
    if aba == ABAS_PLANEJAMENTO[2]:
        st.markdown("**Dados de pecas**")
        col9, col10, col11 = st.columns([1, 2, 1])
        with col9:
            cod_peca = st.text_input("Codigo da peca")
        with col10:
            peca = st.text_input("Descricao da peca")
        with col11:
            qtd_pecas = st.number_input("Qtd. pecas", min_value=0, value=0, step=1)

    confirmar = st.form_submit_button("Criar ordem", use_container_width=True)

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
