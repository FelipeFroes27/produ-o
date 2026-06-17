import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import streamlit as st
from html import escape

from utils.display_mode import ativar_modo_exibicao, render_menu_lateral
from utils.sheets import carregar_historico, carregar_ordens


SENHA_DASHBOARD = "Trendx2026"


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
        .stApp {
            background: #ffffff;
            color: #000000;
        }

        .block-container,
        [data-testid="stMainBlockContainer"] {
            padding-top: 1.05rem !important;
            padding-bottom: 1.25rem !important;
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

        .dashboard-shell,
        .password-shell {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 8px 10px;
            min-height: 0;
        }

        .password-shell {
            margin-bottom: 14px;
            padding: 12px 12px 11px 12px;
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
            height: 22px;
            min-height: 22px;
        }

        .side-title {
            margin: 0 0 8px 0;
            color: #000000;
            font-size: 16px;
            line-height: 1.12;
            font-weight: 900;
            overflow-wrap: anywhere;
        }

        .side-label {
            margin: 10px 0 6px 0;
            color: #000000;
            font-size: 12px;
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
            gap: .22cm !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlockBorder"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 7px !important;
        }

        div[data-testid="stVerticalBlockBorder"] {
            padding: 0 !important;
        }

        .metric-html-card {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 6px 8px;
            margin: 0 0 7px 0;
            box-sizing: border-box;
        }

        .st-key-dashboard_lateral {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            padding: 9px 11px 11px 11px !important;
            min-height: 0;
            height: fit-content !important;
            align-self: flex-start !important;
            box-sizing: border-box;
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
            font-size: 11px;
            font-weight: 850;
            line-height: 1.15;
            white-space: nowrap;
        }

        .metric-line strong {
            font-size: 16px;
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
            border: 2px solid #000000 !important;
            border-color: #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        .st-key-dashboard_lateral [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 8px 10px !important;
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
            margin-bottom: 8px !important;
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
            height: 215px;
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
            min-height: 34px !important;
            margin: 0 0 8px 0 !important;
            font-size: 12px !important;
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


def autenticar_dashboard():
    if st.session_state.get("dashboard_liberado"):
        return True

    modal_senha_dashboard()
    return False


@st.dialog("Acesso ao dashboard")
def modal_senha_dashboard():
    st.markdown(
        """
        <div class="password-shell">
            <h1 class="page-title">Dashboard</h1>
            <p class="page-copy">Informe a senha para acessar o acompanhamento de desempenho.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    senha = st.text_input("Senha", type="password")
    if st.button("Entrar", use_container_width=True):
        if senha == SENHA_DASHBOARD:
            st.session_state.dashboard_liberado = True
            st.rerun()
        else:
            st.error("Senha incorreta.")


aplicar_estilo()
render_sidebar()

if not autenticar_dashboard():
    st.stop()


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

    datas_programacao = programacao["DATA_PRIORIDADE"].dropna() if "DATA_PRIORIDADE" in programacao else pd.Series(dtype="datetime64[ns]")
    datas_historico = historico["DATA"].dropna() if "DATA" in historico else pd.Series(dtype="datetime64[ns]")
    datas_disponiveis = pd.concat([datas_programacao, datas_historico], ignore_index=True).dropna()

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

    if data_inicio is not None and data_fim is not None:
        data_inicio = pd.Timestamp(data_inicio).normalize()
        data_fim = pd.Timestamp(data_fim).normalize()
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

    return programacao, historico

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

    metricas = [
        ("Ordens programadas", total_ordens),
        ("Qtd. programada", formatar_numero(programado)),
        ("Qtd. realizada", formatar_numero(realizado)),
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
        height=236,
        margin=dict(l=42, r=10, t=6, b=34),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#000000", family="Arial", size=10),
        legend_title_text="",
        bargap=0.22,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=10)),
    )
    fig.update_xaxes(showgrid=False, linecolor="#000000", tickfont=dict(color="#000000", size=10), title=None)
    fig.update_yaxes(gridcolor="#e6e6e6", linecolor="#000000", tickfont=dict(color="#000000", size=10), title=None)
    fig.update_traces(marker_line_color="#000000", marker_line_width=1.2)
    return fig


def grafico_pizza_base(fig):
    fig.update_layout(
        height=236,
        margin=dict(l=16, r=16, t=4, b=28),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#000000", family="Arial", size=10),
        legend_title_text="",
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, font=dict(size=10)),
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        insidetextfont=dict(size=10),
        marker=dict(line=dict(color="#000000", width=1.2)),
    )
    return fig


def render_chart(titulo, key, fig=None, vazio="Sem dados para este grafico."):
    if fig is None:
        corpo = f'<div class="empty-chart">{vazio}</div>'
    else:
        corpo = fig.to_html(include_plotlyjs="cdn", full_html=False, config={"displayModeBar": False})

    components.html(
        f"""
        <div style="border:2px solid #000000;border-radius:8px;background:#ffffff;padding:9px 11px 5px 11px;height:278px;box-sizing:border-box;overflow:hidden;font-family:Arial,sans-serif;">
            <div style="font-size:13px;font-weight:900;color:#000000;margin:0 0 4px 0;line-height:1.1;">{titulo}</div>
            <div style="height:246px;">{corpo}</div>
        </div>
        """,
        height=286,
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
    if historico.empty:
        render_chart("Ranking produzido", "chart_atrasadas_usuario", vazio="Aguardando lancamentos.")
        return

    ranking = (
        historico.groupby("USUARIO_RESPONSAVEL", as_index=False)
        .agg(Produzido=("QUANTIDADE_NUM", "sum"))
        .sort_values("Produzido", ascending=False)
    )
    if ranking.empty:
        render_chart("Ranking produzido", "chart_atrasadas_usuario", vazio="Aguardando lancamentos.")
        return

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
    components.html(
        f"""
        <style>
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; font-family: Arial, sans-serif; color: #000; }}
            .card {{
                border: 2px solid #000;
                border-radius: 8px;
                background: #fff;
                height: 278px;
                padding: 9px 11px 8px 11px;
                overflow: hidden;
            }}
            .title {{
                font-size: 13px;
                font-weight: 900;
                margin: 0 0 8px 0;
                line-height: 1.1;
            }}
            .rank-list {{
                display: flex;
                flex-direction: column;
                gap: 7px;
                max-height: 238px;
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
        <div class="card">
            <div class="title">Ranking produzido</div>
            <div class="rank-list">{corpo}</div>
        </div>
        """,
        height=286,
        scrolling=False,
    )

def render_graficos(programacao, historico):
    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        if programacao.empty:
            render_chart("Ordens por usuario", "chart_ordens_usuario")
        else:
            ordens_usuario = (
                programacao.groupby("USUARIO_RESPONSAVEL", as_index=False)
                .agg(Ordens=("OP", "count"))
                .sort_values("Ordens", ascending=False)
            )
            fig = px.bar(
                ordens_usuario,
                x="USUARIO_RESPONSAVEL",
                y="Ordens",
                color="USUARIO_RESPONSAVEL",
                color_discrete_sequence=["#6fb6ff", "#89d47f", "#f2c94c", "#ff8f70", "#b8a3ff"],
            )
            fig = grafico_base(fig)
            fig.update_layout(showlegend=False, margin=dict(l=42, r=10, t=4, b=48))
            fig.update_xaxes(tickangle=-35)
            render_chart("Ordens por usuario", "chart_ordens_usuario", fig)

    with col_2:
        if programacao.empty:
            render_chart("Status das ordens", "chart_status_ordens")
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
            render_chart("Status das ordens", "chart_status_ordens", grafico_pizza_base(fig))

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

    with col_3:
        if comparativo.empty:
            render_chart("Programado x realizado", "chart_programado_realizado")
        else:
            comparativo_longo = comparativo.melt(
                id_vars="USUARIO_RESPONSAVEL",
                value_vars=["Programado", "Realizado", "Pendente"],
                var_name="Indicador",
                value_name="Quantidade",
            )
            fig = px.bar(
                comparativo_longo,
                x="USUARIO_RESPONSAVEL",
                y="Quantidade",
                color="Indicador",
                barmode="group",
                color_discrete_map={
                    "Programado": "#6fb6ff",
                    "Realizado": "#89d47f",
                    "Pendente": "#ff8f70",
                },
            )
            fig = grafico_base(fig)
            fig.update_layout(margin=dict(l=42, r=10, t=4, b=48))
            fig.update_xaxes(tickangle=-35)
            render_chart("Programado x realizado", "chart_programado_realizado", fig)

    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        if programacao.empty:
            render_chart("Ordens por origem", "chart_ordens_origem")
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
            render_chart("Ordens por origem", "chart_ordens_origem", grafico_pizza_base(fig))

    with col_2:
        render_ranking_produzido(historico)

    with col_3:
        historico_com_data = historico[historico["DATA"].notna()] if not historico.empty else pd.DataFrame()
        if historico_com_data.empty:
            render_chart("Realizacoes por dia", "chart_realizacoes_dia")
        else:
            por_dia = (
                historico_com_data.groupby("DATA", as_index=False)
                .agg(Realizado=("QUANTIDADE_NUM", "sum"))
                .sort_values("DATA")
            )
            if len(por_dia) < 2:
                render_chart("Realizacoes por dia", "chart_realizacoes_dia", vazio="Aguardando mais lancamentos.")
            else:
                fig = px.area(
                    por_dia,
                    x="DATA",
                    y="Realizado",
                    markers=True,
                    color_discrete_sequence=["#89d47f"],
                )
                fig.update_traces(line=dict(width=3, color="#111111"), marker=dict(size=7, line=dict(width=1.5, color="#000000")))
                render_chart("Realizacoes por dia", "chart_realizacoes_dia", grafico_base(fig))

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


ordens = carregar_ordens()
historico = preparar_historico(carregar_historico())
programacao = filtrar_programacao(ordens)

st.markdown('<div class="dashboard-top-spacer"></div>', unsafe_allow_html=True)

lateral, graficos = st.columns([0.9, 6.1])

with lateral:
    with st.container(key="dashboard_lateral"):
        st.markdown(
            '<div class="side-title">&#127981; Dashboard<br>Produ&ccedil;&atilde;o</div>',
            unsafe_allow_html=True,
        )
        if st.button("Atualizar dados", key="dashboard_atualizar_dados", use_container_width=True):
            carregar_ordens.clear()
            carregar_historico.clear()
            st.rerun()
        programacao, historico = aplicar_filtros(programacao, historico)
        render_metricas(programacao, historico)

with graficos:
    render_graficos(programacao, historico)
