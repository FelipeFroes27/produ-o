from html import escape

import pandas as pd
import streamlit as st

from utils.display_mode import ativar_modo_exibicao, render_menu_lateral
from utils.sheets import carregar_feriados, carregar_historico, carregar_ordens
from utils.tempo_trabalho import detalhar_horas_comerciais, formatar_duracao_horas, montar_datas_feriados


st.set_page_config(
    page_title="Histórico OP",
    page_icon="icones/consulta-logo-refinado.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("historico_op")
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
            max-width: 1680px;
            padding-top: .7rem;
            padding-bottom: 1.25rem;
        }

        div[data-testid="stVerticalBlock"] {
            gap: .9rem !important;
        }

        .sidebar-logo {
            display: flex;
            gap: 8px;
            align-items: center;
            justify-content: center;
            padding: 8px 0 16px 0;
        }

        .page-title {
            margin: 2.7rem 0 .25rem 0;
            font-size: 30px;
            font-weight: 900;
            color: #000000;
            letter-spacing: 0;
        }

        .page-copy {
            margin: 0 0 1rem 0;
            font-size: 14px;
            color: #1f2937;
        }

        .info-card {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 14px 16px;
            min-height: 104px;
        }

        .info-label {
            margin: 0 0 8px 0;
            font-size: 12px;
            font-weight: 850;
            color: #1f2937;
        }

        .info-value {
            margin: 0;
            font-size: 24px;
            font-weight: 950;
            color: #000000;
            line-height: 1.1;
        }

        .info-note {
            margin: 8px 0 0 0;
            font-size: 12px;
            font-weight: 700;
            color: #374151;
        }

        .section-title {
            margin: .2rem 0 .3rem 0;
            font-size: 17px;
            font-weight: 950;
            color: #000000;
        }

        .explain-box {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #fff7d6;
            padding: 12px 14px;
            font-size: 14px;
            font-weight: 750;
            color: #000000;
            line-height: 1.45;
        }

        .warning-box {
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffe5e5;
            padding: 12px 14px;
            font-size: 14px;
            font-weight: 800;
            color: #000000;
        }

        div[data-testid="stDataFrame"] {
            border: 2px solid #000000;
            border-radius: 8px;
            overflow: hidden;
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
        st.page_link("pages/Historico_OP.py", label="Histórico OP")
        st.page_link("pages/Dashboard.py", label="Dashboard")


def chave_texto(valor):
    return str(valor or "").strip()


def formatar_numero(valor):
    valor = float(valor or 0)
    if valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")


def formatar_data(valor):
    data = pd.to_datetime(valor, dayfirst=True, errors="coerce")
    if pd.isna(data):
        return ""
    return data.strftime("%d/%m/%Y")


def formatar_data_hora(valor):
    data = pd.to_datetime(valor, dayfirst=True, errors="coerce")
    if pd.isna(data):
        return ""
    return data.strftime("%d/%m/%Y %H:%M:%S")


def opcoes_ordens(ordens, historico):
    valores = []
    for base in [ordens, historico]:
        if base is not None and not base.empty and "OP" in base.columns:
            valores.extend(base["OP"].dropna().astype(str).str.strip().tolist())
    return sorted({valor for valor in valores if valor})


def filtrar_op(df, op):
    if df.empty or "OP" not in df.columns:
        return df.iloc[0:0].copy() if not df.empty else df.copy()
    return df[df["OP"].astype(str).str.strip() == op].copy()


def texto_unico(df, coluna):
    if df.empty or coluna not in df.columns:
        return "-"
    valores = [chave_texto(valor) for valor in df[coluna].dropna().tolist() if chave_texto(valor)]
    if not valores:
        return "-"
    unicos = list(dict.fromkeys(valores))
    return ", ".join(unicos[:3]) + ("..." if len(unicos) > 3 else "")


def preparar_lancamentos(historico_op):
    if historico_op.empty:
        return historico_op

    dados = historico_op.copy()
    dados["ACAO_NORM"] = dados["ACAO"].fillna("").astype(str).str.strip().str.upper()
    dados["QUANTIDADE_NUM"] = pd.to_numeric(dados["QUANTIDADE_NUM"], errors="coerce").fillna(0)
    return dados.sort_values("DATA_HORA_DT", na_position="last")


def resumo_tempos(lancamentos, feriados):
    if lancamentos.empty:
        return None

    inicio = lancamentos[lancamentos["ACAO_NORM"] == "INICIO"]["DATA_HORA_DT"].dropna()
    fim = lancamentos[
        (lancamentos["ACAO_NORM"] == "FIM")
        & (lancamentos["QUANTIDADE_NUM"] > 0)
    ]["DATA_HORA_DT"].dropna()

    if inicio.empty or fim.empty:
        return None

    inicio_real = inicio.min()
    fim_real = fim.max()
    if fim_real <= inicio_real:
        return None

    feriados_set = montar_datas_feriados(feriados)
    detalhes = detalhar_horas_comerciais(inicio_real, fim_real, feriados_set)
    horas_uteis = sum(item["HORAS"] for item in detalhes if item["CONTADO"])
    horas_corridas = (fim_real - inicio_real).total_seconds() / 3600

    return {
        "inicio": inicio_real,
        "fim": fim_real,
        "horas_uteis": horas_uteis,
        "horas_corridas": horas_corridas,
        "horas_nao_contadas": max(horas_corridas - horas_uteis, 0),
        "detalhes": detalhes,
    }


def render_card(label, valor, nota=""):
    st.markdown(
        f"""
        <div class="info-card">
            <p class="info-label">{escape(label)}</p>
            <p class="info-value">{escape(str(valor))}</p>
            <p class="info-note">{escape(str(nota))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tabela_programacao(programacao_op):
    if programacao_op.empty:
        return pd.DataFrame()

    colunas = [
        "ABA_ORIGEM",
        "LINHA_PLANILHA",
        "USUARIO_RESPONSAVEL",
        "STATUS",
        "COD_PRODUTO",
        "PRODUTO",
        "QUANTIDADE_NUM",
        "REALIZADO_NUM",
        "SALDO_NUM",
        "DATA_ABERTURA",
        "DATA_PREVISTA",
        "OBS",
    ]
    dados = programacao_op[[coluna for coluna in colunas if coluna in programacao_op.columns]].copy()
    renomear = {
        "ABA_ORIGEM": "Origem",
        "LINHA_PLANILHA": "Linha",
        "USUARIO_RESPONSAVEL": "Usuario",
        "STATUS": "Status",
        "COD_PRODUTO": "Codigo",
        "PRODUTO": "Produto",
        "QUANTIDADE_NUM": "Qtd.",
        "REALIZADO_NUM": "Realizado",
        "SALDO_NUM": "Saldo",
        "DATA_ABERTURA": "Abertura",
        "DATA_PREVISTA": "Previsao",
        "OBS": "Obs.",
    }
    dados = dados.rename(columns=renomear)
    for coluna in ["Qtd.", "Realizado", "Saldo"]:
        if coluna in dados.columns:
            dados[coluna] = dados[coluna].map(formatar_numero)
    for coluna in ["Abertura", "Previsao"]:
        if coluna in dados.columns:
            dados[coluna] = dados[coluna].map(formatar_data)
    return dados


def tabela_historico(lancamentos):
    if lancamentos.empty:
        return pd.DataFrame()

    colunas = ["DATA_HORA_DT", "ACAO", "USUARIO_RESPONSAVEL", "CODIGO", "PRODUTO", "QUANTIDADE_NUM", "TIPO"]
    dados = lancamentos[[coluna for coluna in colunas if coluna in lancamentos.columns]].copy()
    dados = dados.rename(columns={
        "DATA_HORA_DT": "Data/hora",
        "ACAO": "Acao",
        "USUARIO_RESPONSAVEL": "Usuario",
        "CODIGO": "Codigo",
        "PRODUTO": "Produto",
        "QUANTIDADE_NUM": "Quantidade",
        "TIPO": "Tipo",
    })
    if "Data/hora" in dados.columns:
        dados["Data/hora"] = dados["Data/hora"].map(formatar_data_hora)
    if "Quantidade" in dados.columns:
        dados["Quantidade"] = dados["Quantidade"].map(formatar_numero)
    return dados


def tabela_detalhes_tempo(tempos):
    if not tempos:
        return pd.DataFrame()

    dados = pd.DataFrame(tempos["detalhes"])
    if dados.empty:
        return dados
    dados = dados[["DIA", "PERIODO", "INTERVALO", "TEMPO", "OBS"]].rename(columns={
        "DIA": "Dia",
        "PERIODO": "Periodo",
        "INTERVALO": "Intervalo",
        "TEMPO": "Tempo",
        "OBS": "Observacao",
    })
    return dados


aplicar_estilo()
render_sidebar()

st.markdown(
    """
    <h1 class="page-title">Histórico OP</h1>
    <p class="page-copy">Consulta detalhada para entender o que aconteceu com uma ordem de producao.</p>
    """,
    unsafe_allow_html=True,
)

try:
    ordens = carregar_ordens()
    historico = carregar_historico()
    feriados = carregar_feriados()
except Exception as exc:
    st.error("Nao foi possivel carregar os dados do historico.")
    st.caption(str(exc))
    st.stop()

opcoes = opcoes_ordens(ordens, historico)
if not opcoes:
    st.warning("Nenhuma ordem encontrada na programacao ou no historico.")
    st.stop()

op_selecionada = st.selectbox("Ordem de producao", opcoes, key="historico_op_ordem")

programacao_op = filtrar_op(ordens, op_selecionada)
lancamentos = preparar_lancamentos(filtrar_op(historico, op_selecionada))
tempos = resumo_tempos(lancamentos, feriados)

qtd_programada = programacao_op["QUANTIDADE_NUM"].sum() if not programacao_op.empty else 0
qtd_planilha_realizada = programacao_op["REALIZADO_NUM"].sum() if not programacao_op.empty else 0
qtd_historico = (
    lancamentos[(lancamentos["ACAO_NORM"] == "FIM") & (lancamentos["QUANTIDADE_NUM"] > 0)]["QUANTIDADE_NUM"].sum()
    if not lancamentos.empty
    else 0
)
saldo = max(qtd_programada - qtd_planilha_realizada, 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_card("OP", op_selecionada, texto_unico(programacao_op if not programacao_op.empty else lancamentos, "PRODUTO"))
with col2:
    render_card("Quantidade programada", formatar_numero(qtd_programada), f"Saldo atual: {formatar_numero(saldo)}")
with col3:
    render_card("Realizado no historico", formatar_numero(qtd_historico), f"Realizado na planilha: {formatar_numero(qtd_planilha_realizada)}")
with col4:
    tempo_util = formatar_duracao_horas(tempos["horas_uteis"]) if tempos else "-"
    render_card("Tempo util da OP", tempo_util, "Considera turno, sexta, feriados e fins de semana")

col_a, col_b, col_c = st.columns(3)
with col_a:
    render_card("Responsavel", texto_unico(programacao_op if not programacao_op.empty else lancamentos, "USUARIO_RESPONSAVEL"), "")
with col_b:
    render_card("Status", texto_unico(programacao_op, "STATUS"), "")
with col_c:
    render_card("Origem", texto_unico(programacao_op if not programacao_op.empty else lancamentos, "ABA_ORIGEM"), texto_unico(lancamentos, "TIPO"))

if programacao_op["COD_PRODUTO"].nunique() > 1 if not programacao_op.empty and "COD_PRODUTO" in programacao_op.columns else False:
    st.markdown(
        '<div class="warning-box">Esta OP aparece com mais de um codigo de produto na programacao. Confira a planilha.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<p class="section-title">Como o tempo foi calculado</p>', unsafe_allow_html=True)
if tempos:
    inicio_txt = formatar_data_hora(tempos["inicio"])
    fim_txt = formatar_data_hora(tempos["fim"])
    st.markdown(
        f"""
        <div class="explain-box">
            A ordem iniciou em {escape(inicio_txt)} e teve a ultima conclusao em {escape(fim_txt)}.
            O tempo corrido entre esses dois pontos foi {escape(formatar_duracao_horas(tempos["horas_corridas"]))}.
            Para o leadtime, o sistema contou somente {escape(formatar_duracao_horas(tempos["horas_uteis"]))}
            de horario util. O restante, {escape(formatar_duracao_horas(tempos["horas_nao_contadas"]))},
            ficou fora por almoco, noite, sexta apos 17h, fim de semana ou feriado.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="warning-box">Ainda nao existe inicio e fim validos para calcular o tempo desta OP.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<p class="section-title">Detalhamento do tempo util</p>', unsafe_allow_html=True)
detalhes_tempo = tabela_detalhes_tempo(tempos)
if detalhes_tempo.empty:
    st.info("Sem detalhes de tempo para exibir.")
else:
    st.dataframe(detalhes_tempo, hide_index=True, use_container_width=True, height=260)

st.markdown('<p class="section-title">Lancamentos do historico</p>', unsafe_allow_html=True)
historico_tabela = tabela_historico(lancamentos)
if historico_tabela.empty:
    st.info("Esta OP ainda nao possui lancamentos no historico.")
else:
    st.dataframe(historico_tabela, hide_index=True, use_container_width=True, height=300)

st.markdown('<p class="section-title">Programacao vinculada a OP</p>', unsafe_allow_html=True)
programacao_tabela = tabela_programacao(programacao_op)
if programacao_tabela.empty:
    st.info("Esta OP nao foi encontrada nas abas de programacao atuais.")
else:
    st.dataframe(programacao_tabela, hide_index=True, use_container_width=True, height=260)
