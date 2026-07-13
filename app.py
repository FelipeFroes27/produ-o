import base64
from pathlib import Path

import streamlit as st

from utils.display_mode import ativar_modo_exibicao, page_link_icon, render_menu_lateral


st.set_page_config(
    page_title="Controle de Producao",
    page_icon="icones/menu.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ativar_modo_exibicao("inicio")

st.markdown(
    """
    <style>
    header,
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        border: 0 !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    footer, #MainMenu {visibility: hidden;}
    [data-testid="stDecoration"] {display: none !important;}

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
    [data-testid="stSidebar"] span {
        color: #000000 !important;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding-top: .25rem;
        padding-bottom: 1.25rem;
    }

    .home-hero {
        min-height: 300px;
        display: grid;
        grid-template-columns: 1.1fr .9fr;
        gap: .3cm;
        align-items: center;
        padding: 24px;
        border: 2px solid #000000;
        border-radius: 8px;
        background: #ffffff;
        box-shadow: none;
    }

    .brand-row {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        margin-bottom: 22px;
    }

    .brand-row img {
        max-height: 36px;
        max-width: 158px;
        object-fit: contain;
    }

    .brand-row .goper-mark {
        max-height: 36px;
        max-width: 36px;
    }

    .logo-divider {
        width: 3px;
        height: 34px;
        background: #000000;
        display: inline-block;
    }

    .home-title {
        margin: 0;
        color: #000000;
        font-size: 32px;
        line-height: 1.08;
        font-weight: 850;
        letter-spacing: 0;
    }

    .home-copy {
        max-width: 620px;
        margin: 10px 0 0 0;
        color: #333333;
        font-size: 15px;
        line-height: 1.45;
    }

    .home-panel {
        padding: 14px;
        border: 2px solid #000000;
        border-radius: 8px;
        background: #ffffff;
    }

    .home-panel-title {
        margin: 0 0 14px 0;
        color: #000000;
        font-size: 16px;
        font-weight: 850;
    }

    .home-section {
        display: block;
        padding: 11px 12px;
        margin-top: .3cm;
        border-radius: 7px;
        border: 2px solid #000000;
        background: #ffffff;
        color: #000000;
        font-size: 14px;
        font-weight: 800;
    }

    .home-section span {
        display: block;
        margin-top: 3px;
        color: #333333;
        font-size: 12px;
        font-weight: 600;
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

    @media (max-width: 900px) {
        .home-hero {
            grid-template-columns: 1fr;
            padding: 24px;
        }

        .home-title {
            font-size: 28px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_menu_lateral()

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
    page_link_icon("pages/Historico_OP.py", "Histórico OP", "icones/historico.png")
    page_link_icon("pages/Dashboard.py", "Dashboard", "icones/indicadores.png")

logo_branco = base64.b64encode(Path("icones/Logo Branco.bmp").read_bytes()).decode("utf-8")
logo_goper = base64.b64encode(Path("icones/logo preto goper.png").read_bytes()).decode("utf-8")

st.markdown(
    f"""
    <div class="brand-row">
        <img src="data:image/bmp;base64,{logo_branco}" alt="Trendx">
        <span class="logo-divider"></span>
        <img class="goper-mark" src="data:image/png;base64,{logo_goper}" alt="Goper">
    </div>
    <div class="home-hero">
        <div>
            <h1 class="home-title">Sistema de controle de producao</h1>
            <p class="home-copy">
                Menu inicial do sistema para acompanhar demandas, conclusoes e desempenho da producao.
            </p>
        </div>
        <div class="home-panel">
            <div class="home-panel-title">Menu do sistema</div>
            <div class="home-section">
                Producao
                <span>Tela inicial reservada para o controle das ordens de producao.</span>
            </div>
            <div class="home-section">
                Qualidade
                <span>Aprovacao e reprovacao de ordens enviadas para inspecao.</span>
            </div>
            <div class="home-section">
                Embalagens
                <span>Registro de inicio, pausa e conclusao dos itens liberados para embalagem.</span>
            </div>
            <div class="home-section">
                Historico OP
                <span>Consulta detalhada dos lancamentos e do tempo util por ordem.</span>
            </div>
            <div class="home-section">
                Dashboard
                <span>Acompanhamento de desempenho protegido por senha.</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
