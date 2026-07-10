import streamlit as st


MENU_ABERTO_PADRAO = True
MANUTENCAO_ATIVA = False


def page_link_icon(page, label, icon_path):
    col_icon, col_link = st.columns([0.16, 0.84], vertical_alignment="center")
    with col_icon:
        st.image(icon_path, width=18)
    with col_link:
        st.page_link(page, label=label)


def render_menu_lateral():
    if MANUTENCAO_ATIVA:
        _render_manutencao()
        st.stop()

    if "menu_lateral_aberto" not in st.session_state:
        st.session_state.menu_lateral_aberto = MENU_ABERTO_PADRAO

    if st.button("Menu", key="menu_lateral_toggle"):
        st.session_state.menu_lateral_aberto = not st.session_state.menu_lateral_aberto
        st.rerun()

    _aplicar_layout_menu(st.session_state.menu_lateral_aberto)


def ativar_modo_exibicao(pagina_atual):
    _aplicar_css_base()

    st.session_state.modo_exibicao_pagina_atual = pagina_atual

    st.session_state.modo_exibicao_ativo = False
    st.session_state.modo_exibicao_navegando = False
    st.session_state.modo_exibicao_proxima_troca = None


def _render_manutencao():
    st.markdown(
        """
        <style>
        .maintenance-wrap {
            min-height: 72vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px 16px;
        }

        .maintenance-box {
            width: min(760px, 100%);
            border: 2px solid #000000;
            border-radius: 8px;
            background: #ffffff;
            padding: 30px;
            text-align: center;
            color: #000000;
        }

        .maintenance-box h1 {
            margin: 0 0 12px 0;
            font-size: 34px;
            line-height: 1.1;
            font-weight: 900;
        }

        .maintenance-box p {
            margin: 0;
            font-size: 18px;
            line-height: 1.45;
            font-weight: 700;
        }
        </style>
        <div class="maintenance-wrap">
            <div class="maintenance-box">
                <h1>Em manutencao</h1>
                <p>Todas as ordens em processo serao pausadas e retornarao automaticamente.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _aplicar_css_base():
    st.markdown(
        """
        <style>
        header,
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        [data-testid="stHeaderActionElements"],
        [data-testid="stToolbar"],
        [data-testid="stStatusWidget"],
        [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        #MainMenu,
        footer {
            visibility: hidden !important;
        }

        div[data-baseweb="select"],
        div[data-baseweb="select"] *,
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] *,
        div[role="listbox"],
        div[role="listbox"] *,
        [data-testid="stSelectbox"],
        [data-testid="stSelectbox"] * {
            color: #000000 !important;
            opacity: 1 !important;
        }

        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            border-color: #000000 !important;
        }

        div[data-baseweb="select"] svg {
            fill: #000000 !important;
        }

        button,
        div[data-testid="stButton"] button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        div[data-testid="stForm"],
        div[data-testid="stAlert"],
        div[data-testid="stDataFrame"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            overflow: hidden !important;
        }

        div[data-testid="stVerticalBlockBorder"] {
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }

        div[data-testid="stDialog"] div[role="dialog"] {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        iframe[title*="streamlit_autorefresh"],
        div[data-testid="stIFrame"]:has(iframe[title*="streamlit_autorefresh"]),
        div[data-testid="stElementContainer"]:has(iframe[title*="streamlit_autorefresh"]) {
            position: fixed !important;
            width: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: 0 !important;
            opacity: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _aplicar_layout_menu(menu_aberto):
    left = "19.25rem" if menu_aberto else "0.9rem"
    sidebar_css = (
        """
        [data-testid="stAppViewContainer"] {
            overflow-x: visible !important;
        }

        [data-testid="stSidebar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            bottom: 0 !important;
            transform: translateX(0) !important;
            min-width: 18rem !important;
            width: 18rem !important;
            max-width: 18rem !important;
            height: 100vh !important;
            background: #ffffff !important;
            border-right: 1px solid #000000 !important;
            z-index: 999998 !important;
            overflow-y: auto !important;
        }

        [data-testid="stSidebar"] > div,
        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarContent"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: 100% !important;
            min-width: 100% !important;
        }

        [data-testid="stSidebar"] a,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] .sidebar-logo {
            visibility: visible !important;
            opacity: 1 !important;
        }
        """
        if menu_aberto
        else """
        [data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        [data-testid="stAppViewContainer"] > .main {
            margin-left: 0 !important;
        }
        """
    )

    st.markdown(
        f"""
        <style>
        header,
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        [data-testid="stHeaderActionElements"],
        [data-testid="stToolbar"],
        [data-testid="stStatusWidget"],
        [data-testid="stDecoration"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }}

        #MainMenu,
        footer {{
            visibility: hidden !important;
        }}

        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        div[data-baseweb="select"],
        div[data-baseweb="select"] *,
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] *,
        div[role="listbox"],
        div[role="listbox"] *,
        [data-testid="stSelectbox"],
        [data-testid="stSelectbox"] * {{
            color: #000000 !important;
            opacity: 1 !important;
        }}

        div[data-baseweb="select"] > div {{
            background: #ffffff !important;
            border-color: #000000 !important;
        }}

        div[data-baseweb="select"] svg {{
            fill: #000000 !important;
        }}

        button,
        div[data-testid="stButton"] button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        div[data-testid="stForm"],
        div[data-testid="stAlert"],
        div[data-testid="stDataFrame"] {{
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {{
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            overflow: hidden !important;
        }}

        div[data-testid="stVerticalBlockBorder"] {{
            border: 0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stDialog"] div[role="dialog"] {{
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }}

        {sidebar_css}

        .st-key-menu_lateral_toggle {{
            position: fixed !important;
            top: 0.55rem !important;
            left: {left} !important;
            z-index: 999999 !important;
            width: 82px !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        .st-key-menu_lateral_toggle button {{
            min-height: 36px !important;
            padding: 0 14px !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            color: #000000 !important;
            font-weight: 700 !important;
            box-shadow: none !important;
        }}

        .st-key-menu_lateral_toggle button:hover {{
            border-color: #000000 !important;
            color: #000000 !important;
            background: #f2f4f7 !important;
        }}

        .block-container,
        [data-testid="stMainBlockContainer"] {{
            max-width: min(1920px, calc(100vw - 2.5rem)) !important;
            width: 100% !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
            padding-top: 1.15rem !important;
        }}

        div[data-testid="stVerticalBlock"]:has(.st-key-menu_lateral_toggle),
        div[data-testid="stElementContainer"]:has(.st-key-menu_lateral_toggle),
        div[data-testid="stButton"]:has(#menu_lateral_toggle) {{
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
