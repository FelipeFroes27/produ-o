import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import streamlit as st
from html import escape

from utils.display_mode import ativar_modo_exibicao, render_menu_lateral
from utils.sheets import carregar_bd_produtos, carregar_feriados, carregar_historico, carregar_ordens
from utils.tempo_trabalho import calcular_horas_comerciais_intervalos, formatar_duracao_horas, intervalos_ativos_por_lancamentos, montar_datas_feriados


COLUNAS_META_PRODUTO = ["CATEGORIA", "MARCA", "GRUPO"]


st.set_page_config(
    page_title="Dashboard",
    page_icon="icones/consulta-logo-refinado.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("dashboard")
render_menu_lateral()


def aplicar_estilo():
    st.markdown(
        """
        <style>
        :root {
            --dashboard-gap: .3cm;
            --dashboard-card-height: 360px;
        }

        .stApp {
            background: #ffffff;
            color: #000000;
        }

        .block-container,
        [data-testid="stMainBlockContainer"] {
            max-width: 1880px !important;
            padding-top: 1.8rem !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
            padding-bottom: 1.1rem !important;
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

.dashboard-shell {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 8px 10px;
            min-height: 0;
        }

        .dashboard-title {
            margin: 0;
            color: #000000;
            font-size: 17px !important;
            line-height: 1.2;
            font-weight: 850;
            letter-spacing: 0;
        }

        .dashboard-top-spacer {
            height: 52px;
            min-height: 52px;
        }

        .side-title {
            margin: 0 0 10px 0;
            color: #000000;
            font-size: 18px;
            line-height: 1.05;
            font-weight: 900;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .side-label {
            margin: 10px 0 6px 0;
            color: #000000;
            font-size: 13px;
            font-weight: 850;
        }

        .summary-label {
            display: block;
            margin: 16px 0 9px 0;
            padding-top: 2px;
            color: #000000;
            font-size: 13px;
            font-weight: 900;
            line-height: 1.1;
            clear: both;
        }

        .page-title {
            margin: 0;
            color: #000000;
            font-size: 20px !important;
            line-height: 1.08;
            font-weight: 850;
            letter-spacing: 0;
        }

        .page-copy {
            max-width: 780px;
            margin: 6px 0 0 0;
            color: #333333;
            font-size: 12px;
            line-height: 1.25;
        }


        .metric-card,
        .chart-card,
        .table-card {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 8px;
        }

        .metric-label {
            margin: 0;
            font-size: 12px;
            font-weight: 850;
            color: #111111;
        }

        .metric-value {
            margin: 5px 0 3px 0;
            font-size: 20px;
            line-height: 1;
            font-weight: 900;
            color: #000000;
        }

        .metric-help {
            margin: 0;
            font-size: 10px;
            color: #333333;
        }

        .chart-title {
            margin: 0 0 2px 0;
            font-size: 12px;
            font-weight: 900;
            color: #000000;
        }


        div[data-testid="stHorizontalBlock"],
        div[data-testid="stVerticalBlock"] {
            gap: var(--dashboard-gap) !important;
            column-gap: var(--dashboard-gap) !important;
            row-gap: var(--dashboard-gap) !important;
        }

        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        .dashboard-row-gap {
            height: var(--dashboard-gap);
            min-height: var(--dashboard-gap);
        }

        div[data-testid="stIFrame"],
        div[data-testid="stIFrame"] iframe,
        div[data-testid="stElementContainer"]:has(iframe) {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            outline: 0 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            box-shadow: none !important;
            overflow: hidden !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 7px !important;
        }

        div[data-testid="stVerticalBlockBorder"] {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        .metric-html-card {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 8px 9px;
            margin: 0 0 9px 0;
            box-sizing: border-box;
        }

        .st-key-dashboard_lateral {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            padding: 12px 12px 14px 12px !important;
            min-height: 0;
            height: auto !important;
            min-height: calc((var(--dashboard-card-height) * 3) + (var(--dashboard-gap) * 2) + 4px) !important;
            align-self: flex-start !important;
            box-sizing: border-box;
            margin-top: 0 !important;
        }

        .st-key-dashboard_lateral > div {
            min-height: 0 !important;
            height: auto !important;
        }

        .metric-line {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 6px;
            color: #000000;
            font-size: 12px;
            font-weight: 850;
            line-height: 1.15;
            white-space: nowrap;
        }

        .metric-line strong {
            font-size: 18px;
            font-weight: 900;
            white-space: nowrap;
        }

        .ranking-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding-top: 6px;
        }

        .ranking-item {
            display: grid;
            grid-template-columns: 44px 1fr auto;
            align-items: center;
            gap: 10px;
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 8px 10px;
        }

        .ranking-item.first {
            background: #f0fbef;
        }

        .ranking-pos {
            width: 34px;
            height: 34px;
            border: 2px solid #000000;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 900;
            background: #89d47f;
            color: #000000;
        }

        .ranking-name {
            color: #000000;
            font-size: 13px;
            font-weight: 900;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .ranking-value {
            color: #000000;
            font-size: 14px;
            font-weight: 900;
            white-space: nowrap;
        }

        .st-key-dashboard_lateral [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-dashboard_lateral [data-testid="stVerticalBlockBorder"] {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        div[data-testid="stDateInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stDateInput"] input {
            color: #000000 !important;
            font-weight: 750 !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        .st-key-dashboard_lateral div[data-testid="stSelectbox"],
        .st-key-dashboard_lateral div[data-testid="stMultiSelect"],
        .st-key-dashboard_lateral div[data-testid="stDateInput"] {
            margin-bottom: var(--dashboard-gap) !important;
        }

        .st-key-dashboard_lateral div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
            min-height: 48px !important;
            max-height: 112px !important;
            overflow-y: auto !important;
            align-items: flex-start !important;
            padding-top: 3px !important;
            padding-bottom: 3px !important;
        }

        .st-key-dashboard_lateral div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
            max-width: 92px !important;
            height: 29px !important;
            margin: 2px 3px 2px 0 !important;
            border-radius: 7px !important;
        }

        .st-key-dashboard_lateral div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
            max-width: 62px !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }

        .st-key-dashboard_lateral div[data-baseweb="select"]::-webkit-scrollbar {
            width: 7px;
        }

        .st-key-dashboard_lateral div[data-baseweb="select"]::-webkit-scrollbar-track {
            background: #ffffff;
            border-left: 1px solid #000000;
        }

        .st-key-dashboard_lateral div[data-baseweb="select"]::-webkit-scrollbar-thumb {
            background: #ff4b4b;
            border: 1px solid #000000;
            border-radius: 999px;
        }

        div[data-testid="stMarkdownContainer"] p {
            margin-bottom: 0;
        }

        div[data-testid="stMultiSelect"] label {
            font-size: 12px !important;
            font-weight: 800 !important;
        }

        div[data-testid="stMultiSelect"] {
            margin-bottom: 0 !important;
        }

        div[data-testid="stDataFrame"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            overflow: hidden;
        }

        div[data-testid="stAlert"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
        }

        .empty-chart {
            height: 293px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333333;
            font-size: 12px;
            line-height: 1.25;
            text-align: center;
            padding: 0 34px;
            box-sizing: border-box;
        }

        div[data-testid="stTextInput"] input {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stDialog"] div[data-testid="stTextInput"] {
            margin-top: 2px !important;
            margin-bottom: 12px !important;
        }

        div[data-testid="stDialog"] div[data-testid="stTextInput"] label {
            display: block !important;
            padding-bottom: 6px !important;
            color: #000000 !important;
            font-weight: 750 !important;
            line-height: 1.2 !important;
        }

        .stButton button {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            color: #000000 !important;
            font-weight: 850 !important;
            box-shadow: none !important;
        }

        .st-key-dashboard_atualizar_dados button {
            min-height: 38px !important;
            margin: 0 0 8px 0 !important;
            font-size: 13px !important;
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
        st.page_link("pages/Historico_OP.py", label="Histórico OP")
        st.page_link("pages/Dashboard.py", label="Dashboard")


aplicar_estilo()
render_sidebar()


def filtrar_programacao(ordens):
    if ordens.empty:
        return ordens

    programacao = ordens.copy()
    programacao = programacao[
        (programacao["OP"].astype(str).str.strip() != "")
        & (programacao["USUARIO_RESPONSAVEL"].astype(str).str.strip() != "Sem responsavel")
        & (programacao["DATA_PRIORIDADE"].notna())
        & (programacao["QUANTIDADE_NUM"] > 0)
    ].copy()

    return programacao


def chave_texto(valor):
    return str(valor or "").strip().upper()


def enriquecer_produtos(dados, produtos, coluna_codigo, coluna_produto):
    dados = dados.copy()
    for coluna in COLUNAS_META_PRODUTO:
        if coluna not in dados.columns:
            dados[coluna] = ""

    if dados.empty or produtos.empty:
        return dados

    base = produtos.copy()
    for coluna in ["COD_PRODUTO", "PRODUTO", *COLUNAS_META_PRODUTO]:
        if coluna not in base.columns:
            base[coluna] = ""

    meta_codigo = (
        base[base["COD_PRODUTO"].astype(str).str.strip().ne("")]
        .drop_duplicates("COD_PRODUTO")
        .set_index("COD_PRODUTO")[COLUNAS_META_PRODUTO]
    )
    meta_produto = (
        base[base["PRODUTO"].astype(str).str.strip().ne("")]
        .assign(PRODUTO_CHAVE=lambda df: df["PRODUTO"].map(chave_texto))
        .drop_duplicates("PRODUTO_CHAVE")
        .set_index("PRODUTO_CHAVE")[COLUNAS_META_PRODUTO]
    )

    if coluna_codigo in dados.columns and not meta_codigo.empty:
        por_codigo = dados[coluna_codigo].astype(str).str.strip().map(meta_codigo.to_dict("index"))
        for coluna in COLUNAS_META_PRODUTO:
            dados[coluna] = dados[coluna].mask(
                dados[coluna].astype(str).str.strip().eq(""),
                por_codigo.map(lambda valor: valor.get(coluna, "") if isinstance(valor, dict) else ""),
            )

    if coluna_produto in dados.columns and not meta_produto.empty:
        por_produto = dados[coluna_produto].map(chave_texto).map(meta_produto.to_dict("index"))
        for coluna in COLUNAS_META_PRODUTO:
            dados[coluna] = dados[coluna].mask(
                dados[coluna].astype(str).str.strip().eq(""),
                por_produto.map(lambda valor: valor.get(coluna, "") if isinstance(valor, dict) else ""),
            )

    return dados


def opcoes_combobox(serie):
    valores = sorted(
        valor
        for valor in serie.dropna().astype(str).str.strip().unique().tolist()
        if valor
    )
    return ["Todos", *valores]


def aplicar_filtros(programacao, historico):
    usuarios = sorted(
        usuario
        for usuario in set(programacao.get("USUARIO_RESPONSAVEL", pd.Series(dtype=str)).dropna().astype(str))
        if usuario and usuario != "Sem responsavel"
    )
    tipos = sorted(
        tipo
        for tipo in set(programacao.get("ABA_ORIGEM", pd.Series(dtype=str)).dropna().astype(str))
        if tipo
    )

    st.markdown('<p class="side-label">Filtros</p>', unsafe_allow_html=True)
    usuarios_selecionados = st.multiselect("Usuario", usuarios, default=usuarios)
    tipos_selecionados = st.multiselect("Tipo", tipos, default=tipos)

    if usuarios_selecionados:
        programacao = programacao[programacao["USUARIO_RESPONSAVEL"].isin(usuarios_selecionados)]
        historico = historico[historico["USUARIO_RESPONSAVEL"].isin(usuarios_selecionados)]
    else:
        programacao = programacao.iloc[0:0]
        historico = historico.iloc[0:0]

    if tipos_selecionados:
        programacao = programacao[programacao["ABA_ORIGEM"].isin(tipos_selecionados)]
        historico = historico[historico["TIPO"].isin(tipos_selecionados)]
    else:
        programacao = programacao.iloc[0:0]
        historico = historico.iloc[0:0]

    ordem_selecionada = st.selectbox("Ordem", opcoes_combobox(programacao.get("OP", pd.Series(dtype=str))), key="dashboard_filtro_ordem")
    if ordem_selecionada != "Todos":
        programacao = programacao[programacao["OP"].astype(str).str.strip() == ordem_selecionada]
        historico = historico[historico["OP"].astype(str).str.strip() == ordem_selecionada]

    item_selecionado = st.selectbox("Item", opcoes_combobox(programacao.get("PRODUTO", pd.Series(dtype=str))), key="dashboard_filtro_item")
    if item_selecionado != "Todos":
        programacao = programacao[programacao["PRODUTO"].astype(str).str.strip() == item_selecionado]
        historico = historico[historico["PRODUTO"].astype(str).str.strip() == item_selecionado]

    categoria_selecionada = st.selectbox("Categoria", opcoes_combobox(programacao.get("CATEGORIA", pd.Series(dtype=str))), key="dashboard_filtro_categoria")
    if categoria_selecionada != "Todos":
        programacao = programacao[programacao["CATEGORIA"].astype(str).str.strip() == categoria_selecionada]
        historico = historico[historico["CATEGORIA"].astype(str).str.strip() == categoria_selecionada]

    marca_selecionada = st.selectbox("Marca", opcoes_combobox(programacao.get("MARCA", pd.Series(dtype=str))), key="dashboard_filtro_marca")
    if marca_selecionada != "Todos":
        programacao = programacao[programacao["MARCA"].astype(str).str.strip() == marca_selecionada]
        historico = historico[historico["MARCA"].astype(str).str.strip() == marca_selecionada]

    grupo_selecionado = st.selectbox("Grupo", opcoes_combobox(programacao.get("GRUPO", pd.Series(dtype=str))), key="dashboard_filtro_grupo")
    if grupo_selecionado != "Todos":
        programacao = programacao[programacao["GRUPO"].astype(str).str.strip() == grupo_selecionado]
        historico = historico[historico["GRUPO"].astype(str).str.strip() == grupo_selecionado]

    datas_programacao = programacao["DATA_PRIORIDADE"].dropna() if "DATA_PRIORIDADE" in programacao else pd.Series(dtype="datetime64[ns]")
    datas_historico = historico["DATA"].dropna() if "DATA" in historico else pd.Series(dtype="datetime64[ns]")
    datas_disponiveis = pd.concat([datas_programacao, datas_historico], ignore_index=True).dropna()
    datas_disponiveis = pd.to_datetime(datas_disponiveis, errors="coerce").dropna()

    modo_data = st.selectbox("Periodo", ["Tudo", "Mes inteiro", "Dia especifico", "Intervalo"])
    data_inicio = None
    data_fim = None
    if not datas_disponiveis.empty:
        menor_data = datas_disponiveis.min().date()
        maior_data = datas_disponiveis.max().date()
    else:
        hoje = pd.Timestamp.today().date()
        menor_data = hoje
        maior_data = hoje

    meses = {
        "Janeiro": 1,
        "Fevereiro": 2,
        "Mar\u00e7o": 3,
        "Abril": 4,
        "Maio": 5,
        "Junho": 6,
        "Julho": 7,
        "Agosto": 8,
        "Setembro": 9,
        "Outubro": 10,
        "Novembro": 11,
        "Dezembro": 12,
    }
    anos_disponiveis = sorted(set(datas_disponiveis.dt.year.astype(int).tolist())) if not datas_disponiveis.empty else [maior_data.year]

    if modo_data == "Mes inteiro":
        ano = st.selectbox("Ano", anos_disponiveis, index=max(0, anos_disponiveis.index(maior_data.year) if maior_data.year in anos_disponiveis else len(anos_disponiveis) - 1))
        nomes_meses = list(meses.keys())
        mes_nome = st.selectbox("Mes", nomes_meses, index=maior_data.month - 1)
        inicio_mes = pd.Timestamp(year=int(ano), month=meses[mes_nome], day=1)
        data_inicio = inicio_mes
        data_fim = inicio_mes + pd.offsets.MonthEnd(0)
    elif modo_data == "Dia especifico":
        dia = st.date_input("Dia", value=maior_data, format="DD/MM/YYYY")
        data_inicio = pd.Timestamp(dia)
        data_fim = pd.Timestamp(dia)
    elif modo_data == "Intervalo":
        intervalo = st.date_input("Intervalo", value=(menor_data, maior_data), format="DD/MM/YYYY")
        if isinstance(intervalo, tuple) and len(intervalo) == 2:
            data_inicio = pd.Timestamp(intervalo[0])
            data_fim = pd.Timestamp(intervalo[1])

    contexto_periodo = {
        "modo_data": modo_data,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "ordem_filtrada": ordem_selecionada != "Todos",
    }

    if data_inicio is not None and data_fim is not None:
        data_inicio = pd.Timestamp(data_inicio).normalize()
        data_fim = pd.Timestamp(data_fim).normalize()
        contexto_periodo["data_inicio"] = data_inicio
        contexto_periodo["data_fim"] = data_fim
        if "DATA_PRIORIDADE" in programacao:
            programacao = programacao[
                (programacao["DATA_PRIORIDADE"] >= data_inicio)
                & (programacao["DATA_PRIORIDADE"] <= data_fim)
            ]
        if "DATA" in historico:
            historico = historico[
                (historico["DATA"] >= data_inicio)
                & (historico["DATA"] <= data_fim)
            ]

    return programacao, historico, contexto_periodo

def preparar_historico(historico):
    colunas = [
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
    if historico.empty:
        return pd.DataFrame(columns=colunas)

    for coluna in colunas:
        if coluna not in historico.columns:
            historico[coluna] = pd.Series(dtype="object")

    historico = historico.copy()
    historico["USUARIO_RESPONSAVEL"] = historico["USUARIO_RESPONSAVEL"].replace("", "Sem responsavel")
    historico["TIPO"] = historico["TIPO"].replace("", "Sem tipo")
    return historico


def historico_realizado(historico):
    if historico.empty:
        return historico
    if "ACAO" not in historico.columns:
        return historico

    acao = historico["ACAO"].fillna("").astype(str).str.strip().str.upper()
    return historico[
        acao.isin(["PARCIAL", "FIM"])
        | ((acao == "") & (historico["QUANTIDADE_NUM"] > 0))
    ].copy()


def formatar_numero(valor):
    valor = float(valor or 0)
    if valor.is_integer():
        return str(int(valor))
    return str(round(valor, 2)).replace(".", ",")


def render_metricas(programacao, historico):
    total_ordens = len(programacao)
    programado = programacao["QUANTIDADE_NUM"].sum() if not programacao.empty else 0
    realizado = historico["QUANTIDADE_NUM"].sum() if not historico.empty else 0
    atrasadas = int(programacao["ATRASADA"].sum()) if not programacao.empty else 0
    pendente = programacao["SALDO_NUM"].sum() if not programacao.empty else 0

    metricas = [
        ("Ordens programadas", total_ordens),
        ("Qtd. programada", formatar_numero(programado)),
        ("Qtd. realizada", formatar_numero(realizado)),
        ("Qtd. pendente", formatar_numero(pendente)),
        ("Ordens atrasadas", atrasadas),
    ]

    st.markdown('<div class="summary-label">Resumo</div>', unsafe_allow_html=True)
    for titulo, valor in metricas:
        st.markdown(
            f"""
            <div class="metric-html-card">
                <div class="metric-line"><span>{titulo}</span><strong>{valor}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def grafico_base(fig):
    fig.update_layout(
        height=300,
        margin=dict(l=48, r=18, t=20, b=42),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#000000", family="Arial", size=11),
        legend_title_text="",
        bargap=0.22,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=11)),
    )
    fig.update_xaxes(showgrid=False, linecolor="#000000", tickfont=dict(color="#000000", size=11), title=None)
    fig.update_yaxes(gridcolor="#e6e6e6", linecolor="#000000", tickfont=dict(color="#000000", size=11), title=None)
    fig.update_traces(marker_line_color="#000000", marker_line_width=1.2)
    return fig


def aplicar_rotulos_barras(fig):
    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#000000", size=12, family="Arial"),
        cliponaxis=False,
    )
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode="show")
    return fig


def grafico_pizza_base(fig):
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=6, b=34),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#000000", family="Arial", size=11),
        legend_title_text="",
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, font=dict(size=11)),
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        insidetextfont=dict(size=11),
        marker=dict(line=dict(color="#000000", width=1.2)),
    )
    return fig


def render_chart(titulo, key, fig=None, vazio="Sem dados para este grafico.", travado=False):
    components.html(
        montar_chart_html(titulo, fig=fig, vazio=vazio, travado=travado),
        height=368,
        scrolling=False,
    )


def montar_chart_html(titulo, fig=None, vazio="Sem dados para este grafico.", travado=False):
    if fig is None:
        corpo = f'<div class="empty-chart">{vazio}</div>'
    else:
        config = {"displayModeBar": False}
        if travado:
            config.update({"staticPlot": True, "scrollZoom": False, "doubleClick": False})
        corpo = fig.to_html(include_plotlyjs="cdn", full_html=False, config=config)

    return f"""
        <div class="dashboard-card" style="border:2px solid #000000;border-radius:8px;background:#ffffff;padding:10px 12px 6px 12px;height:360px;box-sizing:border-box;overflow:hidden;font-family:Arial,sans-serif;">
            <div style="font-size:14px;font-weight:900;color:#000000;margin:0 0 5px 0;line-height:1.1;">{titulo}</div>
            <div style="height:323px;">{corpo}</div>
        </div>
        """


def render_dashboard_grid(cards):
    grid_css = """
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                color: #000;
                background: #fff;
            }
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: .3cm;
                width: 100%;
                align-items: stretch;
            }
            .dashboard-card {
                width: 100%;
                margin: 0;
            }
            .empty-chart {
                height: 293px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #333;
                font-size: 12px;
                line-height: 1.25;
                text-align: center;
                padding: 0 34px;
            }
        </style>
        """
    components.html(
        f"{grid_css}<div class=\"dashboard-grid\">{''.join(cards)}</div>",
        height=1112,
        scrolling=False,
    )


def ordem_usuarios(df, coluna_usuario):
    if df.empty:
        return []
    return (
        df.groupby(coluna_usuario, as_index=False)
        .size()
        .sort_values("size", ascending=False)[coluna_usuario]
        .tolist()
    )


def render_ranking_produzido(historico):
    components.html(montar_ranking_produzido_html(historico), height=368, scrolling=False)


def montar_ranking_produzido_html(historico):
    if historico.empty:
        return montar_chart_html("Ranking produzido", vazio="Aguardando lancamentos.")

    ranking = (
        historico.groupby("USUARIO_RESPONSAVEL", as_index=False)
        .agg(Produzido=("QUANTIDADE_NUM", "sum"))
        .sort_values("Produzido", ascending=False)
    )
    if ranking.empty:
        return montar_chart_html("Ranking produzido", vazio="Aguardando lancamentos.")

    maior_valor = max(float(ranking["Produzido"].max()), 1)
    cores = ["#f7d154", "#d7dce2", "#d89b63", "#6fb6ff", "#89d47f", "#ff8f70", "#b8a3ff"]
    itens = []
    for indice, linha in enumerate(ranking.itertuples(index=False)):
        posicao = f"{indice + 1}&ordm;"
        cor = cores[indice % len(cores)]
        nome = escape(str(linha.USUARIO_RESPONSAVEL))
        valor_num = float(linha.Produzido)
        valor = formatar_numero(valor_num)
        largura = max(8, min(100, (valor_num / maior_valor) * 100))
        itens.append(
            f"""
            <div class="rank-row">
                <div class="rank-pos" style="background:{cor};">{posicao}</div>
                <div class="rank-main">
                    <div class="rank-top">
                        <span class="rank-name">{nome}</span>
                        <span class="rank-value">{valor}</span>
                    </div>
                    <div class="rank-track"><div class="rank-fill" style="width:{largura}%; background:{cor};"></div></div>
                </div>
            </div>
            """
        )

    corpo = "".join(itens)
    return f"""
        <style>
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; font-family: Arial, sans-serif; color: #000; }}
            .ranking-card {{
                border: 2px solid #000;
                border-radius: 8px;
                background: #fff;
                height: 360px;
                padding: 10px 12px 9px 12px;
                overflow: hidden;
            }}
            .ranking-title {{
                font-size: 14px;
                font-weight: 900;
                margin: 0 0 9px 0;
                line-height: 1.1;
            }}
            .rank-list {{
                display: flex;
                flex-direction: column;
                gap: 7px;
                max-height: 310px;
                overflow-y: auto;
                padding-right: 4px;
            }}
            .rank-list::-webkit-scrollbar {{ width: 8px; }}
            .rank-list::-webkit-scrollbar-track {{
                border: 1px solid #000;
                border-radius: 999px;
                background: #fff;
            }}
            .rank-list::-webkit-scrollbar-thumb {{
                border: 1px solid #000;
                border-radius: 999px;
                background: #89d47f;
            }}
            .rank-row {{
                display: grid;
                grid-template-columns: 42px 1fr;
                align-items: center;
                gap: 9px;
                border: 2px solid #000;
                border-radius: 8px;
                padding: 6px 8px;
                min-height: 40px;
                background: #fff;
            }}
            .rank-pos {{
                width: 30px;
                height: 30px;
                border: 2px solid #000;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 900;
            }}
            .rank-main {{ min-width: 0; }}
            .rank-top {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 4px;
            }}
            .rank-name {{
                font-size: 13px;
                font-weight: 900;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .rank-value {{ font-size: 13px; font-weight: 900; white-space: nowrap; }}
            .rank-track {{ height: 7px; border: 1.5px solid #000; border-radius: 999px; overflow: hidden; background: #fff; }}
            .rank-fill {{ height: 100%; border-right: 1.5px solid #000; }}
        </style>
        <div class="dashboard-card ranking-card">
            <div class="ranking-title">Ranking produzido</div>
            <div class="rank-list">{corpo}</div>
        </div>
        """


def render_programados_produto(programacao, historico):
    components.html(montar_programados_produto_html(programacao, historico), height=368, scrolling=False)


def montar_programados_produto_html(programacao, historico):
    if programacao.empty and historico.empty:
        return montar_chart_html("Itens programados no periodo", vazio="Sem itens programados no periodo.")

    produtos = (
        programacao.groupby(["COD_PRODUTO", "PRODUTO"], as_index=False)
        .agg(Quantidade=("QUANTIDADE_NUM", "sum"), Ordens=("OP", "count"))
        .sort_values(["Quantidade", "Ordens"], ascending=False)
        if not programacao.empty
        else pd.DataFrame(columns=["COD_PRODUTO", "PRODUTO", "Quantidade", "Ordens"])
    )
    realizado_produtos = (
        historico.groupby(["CODIGO", "PRODUTO"], as_index=False)
        .agg(Realizado=("QUANTIDADE_NUM", "sum"))
        .rename(columns={"CODIGO": "COD_PRODUTO"})
        if not historico.empty
        else pd.DataFrame(columns=["COD_PRODUTO", "PRODUTO", "Realizado"])
    )
    produtos = produtos.merge(realizado_produtos, on=["COD_PRODUTO", "PRODUTO"], how="outer")
    produtos["Quantidade"] = produtos["Quantidade"].fillna(produtos["Realizado"]).fillna(0)
    produtos["Realizado"] = produtos["Realizado"].fillna(0)
    produtos["Ordens"] = produtos["Ordens"].fillna(0)
    produtos = (
        produtos[(produtos["Quantidade"] > 0) | (produtos["Realizado"] > 0)]
        .sort_values(["Quantidade", "Realizado", "Ordens"], ascending=False)
        .head(12)
    )
    if produtos.empty:
        return montar_chart_html("Itens programados no periodo", vazio="Sem itens programados no periodo.")

    maior_valor = max(float(produtos["Quantidade"].max()), 1)
    itens = []
    for linha in produtos.itertuples(index=False):
        codigo = escape(str(linha.COD_PRODUTO) or "Sem codigo")
        produto = escape(str(linha.PRODUTO) or "Produto sem descricao")
        quantidade_num = float(linha.Quantidade)
        realizado_num = float(linha.Realizado)
        quantidade = formatar_numero(quantidade_num)
        realizado = formatar_numero(realizado_num)
        ordens = int(linha.Ordens)
        largura_programado = max(7, min(100, (quantidade_num / maior_valor) * 100))
        largura_realizado = min(largura_programado, max(0, (realizado_num / maior_valor) * 100))
        itens.append(
            f"""
            <div class="product-row">
                <div class="product-top">
                    <div class="product-name" title="{produto}">{produto}</div>
                    <div class="product-qty"><span>{realizado}</span> / {quantidade}</div>
                </div>
                <div class="product-meta">Cod. {codigo} | {quantidade} programado | {realizado} realizado | {ordens} ordem(ns)</div>
                <div class="product-track">
                    <div class="product-fill" style="width:{largura_programado}%;"></div>
                    <div class="product-done" style="width:{largura_realizado}%;"></div>
                </div>
            </div>
            """
        )

    return f"""
        <style>
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; font-family: Arial, sans-serif; color: #000; }}
            .product-card {{
                border: 2px solid #000;
                border-radius: 8px;
                background: #fff;
                height: 360px;
                padding: 10px 12px 9px 12px;
                overflow: hidden;
            }}
            .product-title {{
                font-size: 14px;
                font-weight: 900;
                margin: 0 0 9px 0;
                line-height: 1.1;
            }}
            .product-list {{
                display: flex;
                flex-direction: column;
                gap: 8px;
                max-height: 310px;
                overflow-y: auto;
                padding-right: 4px;
            }}
            .product-list::-webkit-scrollbar {{ width: 8px; }}
            .product-list::-webkit-scrollbar-track {{
                border: 1px solid #000;
                border-radius: 999px;
                background: #fff;
            }}
            .product-list::-webkit-scrollbar-thumb {{
                border: 1px solid #000;
                border-radius: 999px;
                background: #6fb6ff;
            }}
            .product-row {{
                border: 2px solid #000;
                border-radius: 8px;
                padding: 7px 9px;
                background: #fff;
            }}
            .product-top {{
                display: grid;
                grid-template-columns: minmax(0, 1fr) auto;
                gap: 10px;
                align-items: center;
            }}
            .product-name {{
                font-size: 13px;
                font-weight: 900;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .product-qty {{
                font-size: 16px;
                font-weight: 900;
                white-space: nowrap;
            }}
            .product-qty span {{
                color: #047857;
            }}
            .product-meta {{
                margin-top: 3px;
                font-size: 11px;
                font-weight: 800;
                color: #333;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .product-track {{
                position: relative;
                height: 8px;
                margin-top: 6px;
                border: 1.5px solid #000;
                border-radius: 999px;
                overflow: hidden;
                background: #fff;
            }}
            .product-fill {{
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                background: #6fb6ff;
                border-right: 1.5px solid #000;
            }}
            .product-done {{
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                background: #89d47f;
                border-right: 1.5px solid #000;
            }}
        </style>
        <div class="dashboard-card product-card">
            <div class="product-title">Itens programados no periodo</div>
            <div class="product-list">{"".join(itens)}</div>
        </div>
        """


def calcular_leadtime(historico, feriados=None):
    colunas = [
        "USUARIO_RESPONSAVEL",
        "CODIGO",
        "PRODUTO",
        "OP",
        "Leadtime_horas",
        "Leadtime_item_total_horas",
        "Quantidade_movimentada",
        "Leadtime_item_horas",
    ]
    if historico.empty or "ACAO" not in historico.columns:
        return pd.DataFrame(columns=colunas)

    dados = historico.copy()
    dados["ACAO_NORM"] = dados["ACAO"].fillna("").astype(str).str.strip().str.upper()
    dados = dados[
        dados["OP"].astype(str).str.strip().ne("")
        & dados["DATA_HORA_DT"].notna()
        & dados["ACAO_NORM"].isin(["INICIO", "PAUSA", "PARCIAL", "FIM"])
    ].copy()
    if dados.empty:
        return pd.DataFrame(columns=colunas)

    chaves = ["USUARIO_RESPONSAVEL", "CODIGO", "PRODUTO", "OP"]
    if "TIPO" in dados.columns:
        chaves.append("TIPO")
    inicio = (
        dados[dados["ACAO_NORM"] == "INICIO"]
        .groupby(chaves, dropna=False)["DATA_HORA_DT"]
        .min()
        .rename("Inicio")
    )
    fim = (
        dados[(dados["ACAO_NORM"] == "FIM") & (dados["QUANTIDADE_NUM"] > 0)]
        .groupby(chaves, dropna=False)["DATA_HORA_DT"]
        .max()
        .rename("Fim")
    )
    movimento = (
        dados[dados["ACAO_NORM"].isin(["PARCIAL", "FIM"]) & (dados["QUANTIDADE_NUM"] > 0)]
        .groupby(chaves, dropna=False)["DATA_HORA_DT"]
        .max()
        .rename("Movimento")
    )
    quantidade = (
        dados[dados["ACAO_NORM"].isin(["PARCIAL", "FIM"]) & (dados["QUANTIDADE_NUM"] > 0)]
        .groupby(chaves, dropna=False)["QUANTIDADE_NUM"]
        .sum()
        .rename("Quantidade_movimentada")
    )
    leadtime = pd.concat([inicio, fim, movimento, quantidade], axis=1).dropna(subset=["Inicio", "Movimento"]).reset_index()
    if leadtime.empty:
        return pd.DataFrame(columns=colunas)

    leadtime = leadtime[leadtime["Movimento"] >= leadtime["Inicio"]].copy()
    leadtime["Quantidade_movimentada"] = pd.to_numeric(leadtime["Quantidade_movimentada"], errors="coerce").fillna(0)
    datas_feriados = montar_datas_feriados(feriados)
    horas_final_por_chave = {}
    horas_item_por_chave = {}
    for chave, grupo in dados.groupby(chaves, dropna=False):
        if not isinstance(chave, tuple):
            chave = (chave,)
        fim_grupo = grupo[(grupo["ACAO_NORM"] == "FIM") & (grupo["QUANTIDADE_NUM"] > 0)]["DATA_HORA_DT"].max()
        movimento_grupo = grupo[
            grupo["ACAO_NORM"].isin(["PARCIAL", "FIM"])
            & (grupo["QUANTIDADE_NUM"] > 0)
        ]["DATA_HORA_DT"].max()
        if pd.notna(fim_grupo):
            intervalos_final = intervalos_ativos_por_lancamentos(grupo, fim_grupo)
            horas_final_por_chave[chave] = calcular_horas_comerciais_intervalos(intervalos_final, datas_feriados)
        if pd.notna(movimento_grupo):
            intervalos_item = intervalos_ativos_por_lancamentos(grupo, movimento_grupo)
            horas_item_por_chave[chave] = calcular_horas_comerciais_intervalos(intervalos_item, datas_feriados)

    leadtime["CHAVE_LEADTIME"] = leadtime[chaves].apply(lambda linha: tuple(linha.tolist()), axis=1)
    leadtime["Leadtime_horas"] = leadtime["CHAVE_LEADTIME"].map(horas_final_por_chave)
    leadtime["Leadtime_item_total_horas"] = leadtime["CHAVE_LEADTIME"].map(horas_item_por_chave).fillna(0)
    leadtime["Leadtime_item_horas"] = leadtime.apply(
        lambda linha: linha["Leadtime_item_total_horas"] / linha["Quantidade_movimentada"]
        if linha["Quantidade_movimentada"] > 0
        else linha["Leadtime_item_total_horas"],
        axis=1,
    )
    return leadtime[colunas]


def render_leadtime_tabela(titulo, leadtime, coluna_nome, vazio, coluna_tempo="Leadtime_horas", total_por_quantidade=False):
    components.html(montar_leadtime_tabela_html(titulo, leadtime, coluna_nome, vazio, coluna_tempo, total_por_quantidade), height=368, scrolling=False)


def montar_leadtime_tabela_html(titulo, leadtime, coluna_nome, vazio, coluna_tempo="Leadtime_horas", total_por_quantidade=False):
    if leadtime.empty:
        return montar_chart_html(titulo, vazio=vazio)

    if coluna_tempo not in leadtime.columns:
        coluna_tempo = "Leadtime_horas"

    if total_por_quantidade:
        coluna_total = "Leadtime_item_total_horas" if "Leadtime_item_total_horas" in leadtime.columns else "Leadtime_horas"
        resumo = (
            leadtime.groupby(coluna_nome, as_index=False)
            .agg(
                Tempo_total_horas=(coluna_total, "sum"),
                Quantidade_total=("Quantidade_movimentada", "sum"),
                Ordens=("OP", "nunique"),
            )
        )
        resumo["Media_horas"] = resumo.apply(
            lambda linha: linha["Tempo_total_horas"] / linha["Quantidade_total"]
            if linha["Quantidade_total"] > 0
            else linha["Tempo_total_horas"],
            axis=1,
        )
        resumo = resumo.sort_values(["Media_horas", "Ordens"], ascending=[True, False]).head(10)
    else:
        leadtime = leadtime[leadtime[coluna_tempo].notna()].copy()
        if leadtime.empty:
            return montar_chart_html(titulo, vazio=vazio)
        resumo = (
            leadtime.groupby(coluna_nome, as_index=False)
            .agg(Media_horas=(coluna_tempo, "mean"), Ordens=("OP", "count"))
            .sort_values(["Media_horas", "Ordens"], ascending=[True, False])
            .head(10)
        )
    if resumo.empty:
        return montar_chart_html(titulo, vazio=vazio)

    linhas = []
    for linha in resumo.itertuples(index=False):
        nome = escape(str(getattr(linha, coluna_nome)) or "Sem identificacao")
        duracao = escape(formatar_duracao_horas(linha.Media_horas))
        ordens = int(linha.Ordens)
        linhas.append(
            f"""
            <div class="lead-row">
                <div class="lead-name" title="{nome}">{nome}</div>
                <div class="lead-time">{duracao}</div>
                <div class="lead-count">{ordens} ordem(ns)</div>
            </div>
            """
        )

    return f"""
        <style>
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; font-family: Arial, sans-serif; color: #000; }}
            .lead-card {{
                border: 2px solid #000;
                border-radius: 8px;
                background: #fff;
                height: 360px;
                padding: 10px 12px 9px 12px;
                overflow: hidden;
            }}
            .lead-title {{
                font-size: 14px;
                font-weight: 900;
                margin: 0 0 9px 0;
                line-height: 1.1;
            }}
            .lead-list {{
                display: flex;
                flex-direction: column;
                gap: 8px;
                max-height: 310px;
                overflow-y: auto;
                padding-right: 4px;
            }}
            .lead-list::-webkit-scrollbar {{ width: 8px; }}
            .lead-list::-webkit-scrollbar-track {{
                border: 1px solid #000;
                border-radius: 999px;
                background: #fff;
            }}
            .lead-list::-webkit-scrollbar-thumb {{
                border: 1px solid #000;
                border-radius: 999px;
                background: #f7d154;
            }}
            .lead-row {{
                display: grid;
                grid-template-columns: minmax(0, 1fr) auto;
                gap: 6px 12px;
                border: 2px solid #000;
                border-radius: 8px;
                background: #fff;
                padding: 8px 10px;
            }}
            .lead-name {{
                grid-column: 1;
                font-size: 13px;
                font-weight: 900;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .lead-time {{
                grid-column: 2;
                grid-row: 1 / span 2;
                align-self: center;
                font-size: 15px;
                font-weight: 900;
                white-space: nowrap;
            }}
            .lead-count {{
                grid-column: 1;
                font-size: 11px;
                font-weight: 800;
                color: #333;
            }}
        </style>
        <div class="dashboard-card lead-card">
            <div class="lead-title">{titulo}</div>
            <div class="lead-list">{"".join(linhas)}</div>
        </div>
        """


def categoria_prazo(linha):
    if bool(linha.get("ATRASADA", False)):
        return "Atrasadas"
    data = linha.get("DATA_PRIORIDADE")
    if pd.isna(data):
        return "Sem data"
    dias = (pd.to_datetime(data).date() - pd.Timestamp.today().date()).days
    if dias == 0:
        return "Hoje"
    if dias <= 5:
        return "Prox. 5 dias"
    return "Futuras"


def render_realizacoes_periodo(historico, contexto_periodo):
    components.html(montar_realizacoes_periodo_html(historico, contexto_periodo), height=368, scrolling=False)


def montar_realizacoes_periodo_html(historico, contexto_periodo):
    historico_com_data = historico[historico["DATA"].notna()] if not historico.empty else pd.DataFrame()
    if historico_com_data.empty:
        return montar_chart_html("Realizacoes por dia")

    if contexto_periodo.get("modo_data") == "Dia especifico":
        historico_com_hora = historico_com_data[historico_com_data["DATA_HORA_DT"].notna()].copy()
        if historico_com_hora.empty:
            return montar_chart_html("Realizacoes por hora", vazio="Sem horario nos lancamentos do dia.")

        hora_decimal = (
            historico_com_hora["DATA_HORA_DT"].dt.hour
            + (historico_com_hora["DATA_HORA_DT"].dt.minute / 60)
        )
        historico_com_hora = historico_com_hora[(hora_decimal >= 8) & (hora_decimal < 19)].copy()
        if historico_com_hora.empty:
            return montar_chart_html("Realizacoes por hora", vazio="Sem lancamentos entre 08h e 18h.")

        hora_decimal = (
            historico_com_hora["DATA_HORA_DT"].dt.hour
            + (historico_com_hora["DATA_HORA_DT"].dt.minute / 60)
        )
        historico_com_hora["HORA_INICIO"] = historico_com_hora["DATA_HORA_DT"].dt.hour.astype(int)
        historico_com_hora["Faixa"] = historico_com_hora["HORA_INICIO"].map(lambda hora: f"{hora:02d}h")

        faixas = [f"{hora:02d}h" for hora in range(8, 19)]
        por_hora = (
            historico_com_hora.groupby("Faixa", as_index=False)
            .agg(Realizado=("QUANTIDADE_NUM", "sum"))
            .set_index("Faixa")
            .reindex(faixas, fill_value=0)
            .reset_index()
        )
        por_hora["Rotulo"] = por_hora["Realizado"].map(formatar_numero)
        fig = px.line(
            por_hora,
            x="Faixa",
            y="Realizado",
            text="Rotulo",
            markers=True,
            color_discrete_sequence=["#111111"],
        )
        fig.update_traces(
            line=dict(width=3, color="#111111"),
            marker=dict(size=8, line=dict(width=1.5, color="#000000"), color="#89d47f"),
            textposition="top center",
            textfont=dict(color="#000000", size=12, family="Arial"),
            cliponaxis=False,
        )
        max_realizado = float(por_hora["Realizado"].max()) if not por_hora.empty else 0
        y_max = max_realizado * 1.22 if max_realizado > 0 else 1
        fig = grafico_base(fig)
        fig.update_layout(margin=dict(l=48, r=18, t=38, b=48))
        fig.update_yaxes(range=[0, y_max])
        return montar_chart_html("Realizacoes por hora", fig=fig, travado=True)

    por_dia = (
        historico_com_data.groupby("DATA", as_index=False)
        .agg(Realizado=("QUANTIDADE_NUM", "sum"))
        .sort_values("DATA")
    )

    data_inicio = contexto_periodo.get("data_inicio")
    data_fim = contexto_periodo.get("data_fim")
    if data_inicio is not None and data_fim is not None:
        dias = pd.date_range(pd.Timestamp(data_inicio), pd.Timestamp(data_fim), freq="D")
        por_dia = (
            por_dia.set_index("DATA")
            .reindex(dias, fill_value=0)
            .rename_axis("DATA")
            .reset_index()
        )

    if len(por_dia) < 2:
        return montar_chart_html("Realizacoes por dia", vazio="Aguardando mais lancamentos.")

    por_dia["Dia"] = pd.to_datetime(por_dia["DATA"]).dt.strftime("%d/%m")
    por_dia["Rotulo"] = por_dia["Realizado"].map(formatar_numero)
    fig = px.line(
        por_dia,
        x="Dia",
        y="Realizado",
        text="Rotulo",
        markers=True,
        color_discrete_sequence=["#111111"],
    )
    fig.update_traces(
        line=dict(width=3, color="#111111"),
        marker=dict(size=8, line=dict(width=1.5, color="#000000"), color="#89d47f"),
        textposition="top center",
        textfont=dict(color="#000000", size=12, family="Arial"),
        cliponaxis=False,
    )
    max_realizado = float(por_dia["Realizado"].max()) if not por_dia.empty else 0
    y_max = max_realizado * 1.22 if max_realizado > 0 else 1
    fig = grafico_base(fig)
    fig.update_layout(margin=dict(l=48, r=18, t=38, b=48))
    fig.update_yaxes(range=[0, y_max])
    return montar_chart_html("Realizacoes por dia", fig=fig, travado=True)


def render_graficos(programacao, historico, contexto_periodo, historico_leadtime=None, feriados=None):
    historico_leadtime = historico if historico_leadtime is None else historico_leadtime
    leadtime = calcular_leadtime(historico_leadtime, feriados)

    cards = []

    if programacao.empty:
        cards.append(montar_chart_html("Ordens por usuario"))
    else:
        ordens_usuario = (
            programacao.groupby("USUARIO_RESPONSAVEL", as_index=False)
            .agg(Ordens=("OP", "count"))
            .sort_values("Ordens", ascending=False)
        )
        ordens_usuario["Rotulo"] = ordens_usuario["Ordens"].map(formatar_numero)
        fig = px.bar(
            ordens_usuario,
            x="USUARIO_RESPONSAVEL",
            y="Ordens",
            color="USUARIO_RESPONSAVEL",
            text="Rotulo",
            color_discrete_sequence=["#6fb6ff", "#89d47f", "#f2c94c", "#ff8f70", "#b8a3ff"],
        )
        fig = aplicar_rotulos_barras(grafico_base(fig))
        fig.update_layout(showlegend=False, margin=dict(l=48, r=18, t=24, b=52))
        fig.update_xaxes(tickangle=-35)
        cards.append(montar_chart_html("Ordens por usuario", fig=fig))

    if programacao.empty:
        cards.append(montar_chart_html("Status das ordens"))
    else:
        status_ordens = (
            programacao.groupby("STATUS", as_index=False)
            .agg(Ordens=("OP", "count"))
            .sort_values("Ordens", ascending=False)
        )
        fig = px.pie(
            status_ordens,
            names="STATUS",
            values="Ordens",
            hole=0.58,
            color_discrete_sequence=["#ff8f70", "#89d47f", "#f2c94c", "#6fb6ff"],
        )
        cards.append(montar_chart_html("Status das ordens", fig=grafico_pizza_base(fig)))

    comparativo_programado = (
        programacao.groupby("USUARIO_RESPONSAVEL", as_index=False)
        .agg(Programado=("QUANTIDADE_NUM", "sum"), Pendente=("SALDO_NUM", "sum"))
        if not programacao.empty
        else pd.DataFrame(columns=["USUARIO_RESPONSAVEL", "Programado", "Pendente"])
    )
    comparativo_realizado = (
        historico.groupby("USUARIO_RESPONSAVEL", as_index=False)
        .agg(Realizado=("QUANTIDADE_NUM", "sum"))
        if not historico.empty
        else pd.DataFrame(columns=["USUARIO_RESPONSAVEL", "Realizado"])
    )
    comparativo = comparativo_programado.merge(comparativo_realizado, on="USUARIO_RESPONSAVEL", how="outer").fillna(0)

    if comparativo.empty:
        cards.append(montar_chart_html("Programado x realizado"))
    else:
        comparativo_longo = comparativo.melt(
            id_vars="USUARIO_RESPONSAVEL",
            value_vars=["Programado", "Realizado", "Pendente"],
            var_name="Indicador",
            value_name="Quantidade",
        )
        comparativo_longo["Rotulo"] = comparativo_longo["Quantidade"].map(formatar_numero)
        fig = px.bar(
            comparativo_longo,
            x="USUARIO_RESPONSAVEL",
            y="Quantidade",
            color="Indicador",
            barmode="group",
            text="Rotulo",
            color_discrete_map={
                "Programado": "#6fb6ff",
                "Realizado": "#89d47f",
                "Pendente": "#ff8f70",
            },
        )
        fig = aplicar_rotulos_barras(grafico_base(fig))
        fig.update_layout(margin=dict(l=48, r=18, t=24, b=52))
        fig.update_xaxes(tickangle=-35)
        cards.append(montar_chart_html("Programado x realizado", fig=fig))

    if programacao.empty:
        cards.append(montar_chart_html("Ordens por origem"))
    else:
        origem = (
            programacao.groupby("ABA_ORIGEM", as_index=False)
            .agg(Ordens=("OP", "count"))
            .sort_values("Ordens", ascending=False)
        )
        fig = px.pie(
            origem,
            names="ABA_ORIGEM",
            values="Ordens",
            hole=0.0,
            color_discrete_sequence=["#6fb6ff", "#f2c94c", "#89d47f", "#ff8f70"],
        )
        cards.append(montar_chart_html("Ordens por origem", fig=grafico_pizza_base(fig)))

    cards.append(montar_ranking_produzido_html(historico))
    cards.append(montar_realizacoes_periodo_html(historico, contexto_periodo))
    cards.append(montar_programados_produto_html(programacao, historico))
    cards.append(
        montar_leadtime_tabela_html(
            "Tempo medio por usuario",
            leadtime,
            "USUARIO_RESPONSAVEL",
            "Aguardando ordens com inicio e fim.",
            "Leadtime_horas",
        )
    )
    cards.append(
        montar_leadtime_tabela_html(
            "Tempo medio por produto",
            leadtime,
            "PRODUTO",
            "Aguardando produtos com inicio e fim.",
            "Leadtime_item_horas",
            total_por_quantidade=True,
        )
    )
    render_dashboard_grid(cards)

def render_tabela_resumo(programacao, historico):
    if programacao.empty:
        with st.container(border=True):
            st.markdown('<p class="chart-title">Resumo por usuario</p>', unsafe_allow_html=True)
        return

    resumo = (
        programacao.groupby("USUARIO_RESPONSAVEL", as_index=False)
        .agg(
            Ordens=("OP", "count"),
            Programado=("QUANTIDADE_NUM", "sum"),
            Pendente=("SALDO_NUM", "sum"),
            Atrasadas=("ATRASADA", "sum"),
        )
    )
    realizado = (
        historico.groupby("USUARIO_RESPONSAVEL", as_index=False)
        .agg(Realizado=("QUANTIDADE_NUM", "sum"))
        if not historico.empty
        else pd.DataFrame(columns=["USUARIO_RESPONSAVEL", "Realizado"])
    )
    resumo = resumo.merge(realizado, on="USUARIO_RESPONSAVEL", how="left").fillna(0)
    resumo["Aproveitamento"] = resumo.apply(
        lambda linha: f"{round((linha['Realizado'] / linha['Programado']) * 100, 1)}%" if linha["Programado"] else "0%",
        axis=1,
    )
    resumo = resumo.rename(
        columns={
            "USUARIO_RESPONSAVEL": "Usuario",
            "Programado": "Qtd. programada",
            "Realizado": "Qtd. realizada",
            "Pendente": "Qtd. pendente",
        }
    )
    for coluna in ["Qtd. programada", "Qtd. realizada", "Qtd. pendente"]:
        resumo[coluna] = resumo[coluna].map(formatar_numero)

    with st.container(border=True):
        st.markdown('<p class="chart-title">Resumo por usuario</p>', unsafe_allow_html=True)
        st.dataframe(
            resumo[["Usuario", "Ordens", "Qtd. programada", "Qtd. realizada", "Qtd. pendente", "Atrasadas", "Aproveitamento"]],
            hide_index=True,
            use_container_width=True,
        )


try:
    ordens = carregar_ordens()
    bd_produtos = carregar_bd_produtos()
    feriados = carregar_feriados()
    historico = preparar_historico(carregar_historico())
except Exception as exc:
    st.error("Nao foi possivel carregar os dados do dashboard.")
    st.caption(str(exc))
    st.stop()

programacao = filtrar_programacao(ordens)
programacao = enriquecer_produtos(programacao, bd_produtos, "COD_PRODUTO", "PRODUTO")
historico = enriquecer_produtos(historico, bd_produtos, "CODIGO", "PRODUTO")

st.markdown('<div class="dashboard-top-spacer"></div>', unsafe_allow_html=True)

lateral, graficos = st.columns([1.28, 6.72], gap="small", vertical_alignment="top")

with lateral:
    with st.container(key="dashboard_lateral"):
        st.image("dashboard.png", use_container_width=True)
        if st.button("Atualizar dados", key="dashboard_atualizar_dados", use_container_width=True):
            carregar_ordens.clear()
            carregar_historico.clear()
            carregar_bd_produtos.clear()
            carregar_feriados.clear()
            st.rerun()
        programacao, historico, contexto_periodo = aplicar_filtros(programacao, historico)
        historico_fim = historico_realizado(historico)
        render_metricas(programacao, historico_fim)

with graficos:
    render_graficos(programacao, historico_fim, contexto_periodo, historico, feriados)
