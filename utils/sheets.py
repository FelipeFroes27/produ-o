import threading
import unicodedata
from datetime import datetime, timedelta, timezone

import gspread
import pandas as pd
import streamlit as st
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials


_SHEETS_LOCK = threading.RLock()

SPREADSHEET_ID = "10_J6pYgEcQNNQjwWIZCaeNPeOo928GoQ3zENwpLtWSc"
ABAS_PLANEJAMENTO = ["Produ\u00e7\u00e3o", "Manuten\u00e7\u00e3o", "Pe\u00e7as"]
ABA_USUARIOS = "Usu\u00e1rios"
ABA_HISTORICO = "Hist\u00f3rico"
ABA_BD_PRODUTOS = "Bd_produtos"
ABA_FERIADOS = "Feriados"
FUSO_BRASILIA = timezone(timedelta(hours=-3))
COLUNAS_USUARIOS = ["Codigo", "Nome", "Cargo"]
COLUNAS_ORDENS = [
    "USUARIO_RESPONSAVEL",
    "STATUS",
    "OP",
    "COD_PRODUTO",
    "PRODUTO",
    "COD_PECA",
    "PECA",
    "QTD_PECAS",
    "QUANTIDADE",
    "REALIZADO",
    "DATA_ABERTURA",
    "DATA_PREVISTA",
    "DATA",
    "OBS",
    "ABA_ORIGEM",
    "LINHA_PLANILHA",
    "PECAS_BLOCO",
    "QUANTIDADE_NUM",
    "REALIZADO_NUM",
    "SALDO_NUM",
    "DATA_PRIORIDADE",
    "DIAS_ATRASO",
    "ATRASADA",
]
COLUNAS_HISTORICO = [
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
COLUNAS_PRODUTOS = [
    "COD_PRODUTO",
    "PRODUTO",
    "CATEGORIA",
    "MARCA",
    "GRUPO",
]
COLUNAS_FERIADOS = ["DATA"]
ETAPAS_PLANEJAMENTO = ["PRODUCAO", "MANUTENCAO", "PECAS"]
CABECALHOS_PLANEJAMENTO = {
    "Produção": ["DATA_ABERTURA", "N° DA OP", "COD_PRODUTO", "DESCRIÇÃO", "QUANTIDADE", "OBS", "DATA_PREVISTA", "REALIZADO", "STATUS", "USUÁRIO RESPONSAVEL"],
    "Manutenção": ["DATA", "N° DA OP", "COD_PRODUTO", "DESCRIÇÃO", "OBS", "QUANTIDADE", "REALIZADO", "STATUS", "USUÁRIO RESPONSAVEL"],
    "Peças": ["DATA", "N° DA OP", "COD_PRODUTO", "DESCRIÇÃO", "COD_PEÇA", "DESCRIÇÃO PEÇA", "QTD_PEÇAS", "QUANTIDADE", "REALIZADO", "STATUS", "USUÁRIO RESPONSAVEL"],
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def conectar():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


@st.cache_resource
def abrir_planilha():
    return conectar().open_by_key(SPREADSHEET_ID)


def acao_descritiva(acao, etapa=""):
    acao_texto = str(acao or "").strip().title()
    etapa_texto = str(etapa or "").strip()
    if not acao_texto:
        return ""
    if not etapa_texto:
        return acao_texto
    return f"{acao_texto} {etapa_texto}"


def acao_base_historico(acao):
    acao_norm = _normalizar(acao)
    for base in ["ENTRADA", "INICIO", "PAUSA", "PARCIAL", "FIM", "QUALIDADE", "APROVADO", "REPROVADO", "EMBALAGEM"]:
        if acao_norm == base or acao_norm.startswith(base):
            return base
    return acao_norm


def acao_etapa_historico(acao):
    acao_norm = _normalizar(acao)
    base = acao_base_historico(acao)
    if not base:
        return ""
    if acao_norm == base:
        if base in ["QUALIDADE", "APROVADO", "REPROVADO"]:
            return "QUALIDADE"
        if base == "EMBALAGEM":
            return "EMBALAGEM"
        return ""
    return _normalizar_etapa_historico(acao_norm[len(base):].strip())


def _normalizar_etapa_historico(etapa):
    etapa_norm = _normalizar(etapa)
    if etapa_norm.startswith("PRODU"):
        return "PRODUCAO"
    if etapa_norm.startswith("MANUTEN"):
        return "MANUTENCAO"
    if etapa_norm.startswith("PEC") or etapa_norm.startswith("PEA") or etapa_norm == "PEAS":
        return "PECAS"
    if etapa_norm.startswith("QUALIDADE"):
        return "QUALIDADE"
    if etapa_norm.startswith("EMBALAGEM"):
        return "EMBALAGEM"
    return etapa_norm


def acao_produtiva_historico(acao):
    return acao_base_historico(acao) in ["PARCIAL", "FIM"] and acao_etapa_historico(acao) in ETAPAS_PLANEJAMENTO


@st.cache_data(ttl=180)
def carregar_usuarios():
    worksheet = abrir_planilha().worksheet(ABA_USUARIOS)
    df = pd.DataFrame(worksheet.get_all_records(numericise_ignore=["all"]))
    df = _limpar_dataframe(df)
    df = _padronizar_usuarios(df)

    if "Codigo" in df.columns:
        df = df[df["Codigo"].astype(str).str.strip() != ""]
    if "Nome" in df.columns:
        df = df[df["Nome"].astype(str).str.strip() != ""]

    return df


@st.cache_data(ttl=180)
def carregar_ordens():
    frames = []

    for nome_aba in ABAS_PLANEJAMENTO:
        worksheet = abrir_planilha().worksheet(nome_aba)
        values = worksheet.get_all_values()
        if not values:
            continue

        headers = [str(coluna).strip() for coluna in values[0]]
        rows = []
        for row_index, row in enumerate(values[1:], start=2):
            registro = {
                header: str(row[pos]).strip() if pos < len(row) else ""
                for pos, header in enumerate(headers)
                if header
            }
            registro["ABA_ORIGEM"] = nome_aba
            registro["LINHA_PLANILHA"] = row_index
            rows.append(registro)

        df = pd.DataFrame(rows)
        df = _limpar_dataframe(df)
        df = _remover_linhas_de_cabecalho_repetido(df)
        if nome_aba == "Pe\u00e7as":
            df = _vincular_pecas_a_ordem(df)
        frames.append(df)

    if not frames:
        return _ordens_vazias()

    ordens = pd.concat(frames, ignore_index=True, sort=False)
    return _padronizar_ordens(ordens)


def carregar_resumo():
    return carregar_usuarios(), carregar_ordens()


@st.cache_data(ttl=180)
def carregar_historico():
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    values = worksheet.get_all_values()
    if not values:
        return _historico_vazio()

    headers = [str(coluna).strip() for coluna in values[0]]
    rows = []
    for row in values[1:]:
        registro = {
            header: str(row[pos]).strip() if pos < len(row) else ""
            for pos, header in enumerate(headers)
            if header
        }
        rows.append(registro)

    df = pd.DataFrame(rows)
    df = _limpar_dataframe(df)
    if df.empty:
        return _historico_vazio()

    colunas = {
        "USUARIO_RESPONSAVEL": _encontrar_coluna(df, ["USUÁRIO RESPONSAVEL", "USUARIO RESPONSAVEL"]),
        "OP": _encontrar_coluna(df, ["N° DA OP", "N DA OP", "OP"]),
        "DATA_HORA": _encontrar_coluna(df, ["DATA / HORA", "DATA HORA"]),
        "CODIGO": _encontrar_coluna(df, ["CODIGO"]),
        "PRODUTO": _encontrar_coluna(df, ["PRODUTO"]),
        "QUANTIDADE": _encontrar_coluna(df, ["QUANTIDADE"]),
        "TIPO": _encontrar_coluna(df, ["TIPO"]),
        "ACAO": _encontrar_coluna(df, ["A\u00c7\u00c3O", "ACAO"]),
    }

    for nome_padrao, coluna_origem in colunas.items():
        if coluna_origem is None:
            df[nome_padrao] = ""
        else:
            df[nome_padrao] = df[coluna_origem].astype(str).str.strip()

    campos_chave = ["USUARIO_RESPONSAVEL", "OP", "CODIGO", "PRODUTO", "QUANTIDADE", "TIPO"]
    tem_dados = df[campos_chave].apply(lambda linha: any(str(valor).strip() for valor in linha), axis=1)
    df = df[tem_dados].copy()
    df["QUANTIDADE_NUM"] = _serie_numero(df["QUANTIDADE"])
    df["DATA_HORA_DT"] = pd.to_datetime(df["DATA_HORA"], dayfirst=True, errors="coerce")
    df["DATA"] = df["DATA_HORA_DT"].dt.normalize()
    df["ACAO_BASE"] = df["ACAO"].map(acao_base_historico)
    df["ACAO_ETAPA"] = df["ACAO"].map(acao_etapa_historico)

    return _garantir_colunas(df, COLUNAS_HISTORICO)


@st.cache_data(ttl=180)
def carregar_bd_produtos():
    try:
        worksheet = abrir_planilha().worksheet(ABA_BD_PRODUTOS)
    except Exception:
        return _produtos_vazios()

    values = worksheet.get_all_values()
    if not values:
        return _produtos_vazios()

    headers = [str(coluna).strip() for coluna in values[0]]
    rows = []
    for row in values[1:]:
        registro = {
            header: str(row[pos]).strip() if pos < len(row) else ""
            for pos, header in enumerate(headers)
            if header
        }
        rows.append(registro)

    df = pd.DataFrame(rows)
    df = _limpar_dataframe(df)
    if df.empty:
        return _produtos_vazios()

    return _padronizar_produtos(df)


@st.cache_data(ttl=180)
def carregar_feriados():
    try:
        worksheet = abrir_planilha().worksheet(ABA_FERIADOS)
    except Exception:
        return _feriados_vazios()

    values = worksheet.get_all_values()
    if not values:
        return _feriados_vazios()

    headers = [str(coluna).strip() for coluna in values[0]]
    rows = []
    for row in values[1:]:
        registro = {
            header: str(row[pos]).strip() if pos < len(row) else ""
            for pos, header in enumerate(headers)
            if header
        }
        rows.append(registro)

    df = pd.DataFrame(rows)
    df = _limpar_dataframe(df)
    if df.empty:
        return _feriados_vazios()

    coluna_data = _encontrar_coluna(df, ["DATA"])
    if coluna_data is None:
        return _feriados_vazios()

    feriados = pd.DataFrame({
        "DATA": pd.to_datetime(df[coluna_data], dayfirst=True, errors="coerce").dt.normalize()
    })
    feriados = feriados[feriados["DATA"].notna()].drop_duplicates(subset=["DATA"]).copy()
    if feriados.empty:
        return _feriados_vazios()

    return _garantir_colunas(feriados, COLUNAS_FERIADOS)


def lancar_realizacao(ordem, quantidade_lancada, qualidade=False):
    aba_origem = str(ordem["ABA_ORIGEM"])
    linha_planilha = int(ordem["LINHA_PLANILHA"])
    quantidade_lancada = float(quantidade_lancada)

    if quantidade_lancada <= 0:
        raise ValueError("Informe uma quantidade maior que zero.")

    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_controle_ordem(ordem)
        if ultima_acao != "INICIO":
            if ultima_acao == "PAUSA":
                raise ValueError("Retome a ordem antes de concluir.")
            raise ValueError("Inicie a ordem antes de concluir.")

        worksheet = abrir_planilha().worksheet(aba_origem)
        headers = worksheet.row_values(1)
        _confirmar_linha_ordem(worksheet, headers, linha_planilha, ordem)
        coluna_realizado = _indice_coluna(headers, "REALIZADO")
        realizado_atual = _numero_celula(worksheet.cell(linha_planilha, coluna_realizado).value)
        saldo = max(float(ordem["QUANTIDADE_NUM"]) - realizado_atual, 0)

        if quantidade_lancada > saldo:
            raise ValueError(f"A quantidade lancada passa do saldo pendente ({_formatar_numero(saldo)}).")

        novo_realizado = realizado_atual + quantidade_lancada
        quantidade_total = float(ordem["QUANTIDADE_NUM"])
        acao = acao_descritiva("Fim" if novo_realizado >= quantidade_total else "Parcial", ordem.get("ABA_ORIGEM", ""))

        worksheet.update_cell(linha_planilha, coluna_realizado, _formatar_numero(novo_realizado))
        try:
            registros = [{
                "ordem": ordem,
                "quantidade": quantidade_lancada,
                "acao": acao,
            }]
            if qualidade:
                registros.append({
                    "ordem": ordem,
                    "quantidade": quantidade_lancada,
                    "acao": acao_descritiva("Entrada", "Qualidade"),
                })
            registrar_historico_lote(registros)
        except Exception as exc:
            try:
                worksheet.update_cell(linha_planilha, coluna_realizado, _formatar_numero(realizado_atual))
                carregar_ordens.clear()
            except Exception:
                pass
            raise RuntimeError("A ordem foi restaurada porque nao foi possivel registrar o historico. Tente novamente.") from exc

    carregar_ordens.clear()


def lancar_encaminhamento_qualidade(ordem, quantidade):
    quantidade = float(quantidade)
    if quantidade <= 0:
        raise ValueError("Informe uma quantidade maior que zero.")
    registrar_historico(ordem, quantidade, acao_descritiva("Entrada", "Qualidade"))
    carregar_historico.clear()


def lancar_encaminhamento_embalagem(ordem, quantidade):
    quantidade = float(quantidade)
    if quantidade <= 0:
        raise ValueError("Informe uma quantidade maior que zero.")
    registrar_historico(ordem, quantidade, acao_descritiva("Entrada", "Embalagem"))
    carregar_historico.clear()


def _confirmar_op_disponivel(values, headers, op_nova):
    op_nova_norm = _normalizar(op_nova)
    if not op_nova_norm:
        return

    col_op = _indice_coluna_opcional(headers, ["N° DA OP", "N DA OP", "OP"])
    if not col_op:
        return

    indice = col_op - 1
    for row in values[1:]:
        valor_op = str(row[indice]).strip() if indice < len(row) else ""
        if valor_op and _normalizar(valor_op) == op_nova_norm:
            raise ValueError(
                f"Ja existe uma ordem com o numero de OP {op_nova} nesta aba. "
                "Atualize a pagina para obter um novo numero sugerido e tente novamente."
            )


def criar_ordem_planejamento(aba, dados):
    aba = str(aba or "").strip()
    if aba not in ABAS_PLANEJAMENTO:
        raise ValueError("Escolha uma aba de planejamento valida.")

    with _SHEETS_LOCK:
        worksheet = abrir_planilha().worksheet(aba)
        headers = [str(header).strip() for header in worksheet.row_values(1) if str(header).strip()]
        if not headers:
            headers = CABECALHOS_PLANEJAMENTO[aba]
        valores = _montar_linha_planejamento(aba, headers, dados)
        data_bloco = _data_bloco_ordem(aba, dados)
        if pd.isna(data_bloco):
            raise ValueError("Informe uma data valida para posicionar a ordem no planejamento.")

        values = worksheet.get_all_values()
        _confirmar_op_disponivel(values, headers, dados.get("OP", ""))
        destino = _localizar_insercao_planejamento(values, headers, data_bloco)
        linhas = []
        if destino["novo_bloco"]:
            linhas.append(headers)
        linhas.extend([valores, [""] * len(headers)])

        worksheet.insert_rows(linhas, row=destino["linha"], value_input_option="USER_ENTERED")
        _copiar_formatos_planejamento(worksheet, destino["linha"], len(headers), destino["novo_bloco"])
    carregar_ordens.clear()
    return {
        "aba": aba,
        "linha": destino["linha"] + (1 if destino["novo_bloco"] else 0),
        "novo_bloco": destino["novo_bloco"],
    }


def lancar_inicio_ordem(ordem):
    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_controle_ordem(ordem)
        if ultima_acao == "INICIO":
            raise ValueError("Esta ordem ja esta em andamento.")
        registrar_historico(ordem, 0, acao_descritiva("Inicio", ordem.get("ABA_ORIGEM", "")))
    carregar_historico.clear()


def lancar_pausa_ordem(ordem):
    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_controle_ordem(ordem)
        if ultima_acao != "INICIO":
            if ultima_acao == "PAUSA":
                raise ValueError("Esta ordem ja esta pausada.")
            raise ValueError("Inicie a ordem antes de pausar.")
        registrar_historico(ordem, 0, acao_descritiva("Pausa", ordem.get("ABA_ORIGEM", "")))
    carregar_historico.clear()


def lancar_inicio_setor(ordem, setor, usuario=""):
    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_setor_ordem(ordem, setor)
        if ultima_acao == "INICIO":
            raise ValueError(f"Esta etapa de {str(setor).lower()} ja esta em andamento.")
        registrar_historico(
            ordem,
            0,
            acao_descritiva("Inicio", setor),
            avaliador=usuario,
            usuario_responsavel=usuario,
        )
    carregar_historico.clear()


def lancar_pausa_setor(ordem, setor, usuario=""):
    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_setor_ordem(ordem, setor)
        if ultima_acao != "INICIO":
            if ultima_acao == "PAUSA":
                raise ValueError(f"Esta etapa de {str(setor).lower()} ja esta pausada.")
            raise ValueError(f"Inicie a etapa de {str(setor).lower()} antes de pausar.")
        usuario = usuario or ultimo_inicio_ativo_setor_ordem(ordem, setor)
        if not usuario:
            raise ValueError(f"Nao foi possivel identificar o usuario que iniciou a etapa de {str(setor).lower()}.")
        registrar_historico(
            ordem,
            0,
            acao_descritiva("Pausa", setor),
            avaliador=usuario,
            usuario_responsavel=usuario,
        )
    carregar_historico.clear()


def lancar_movimento_setor(ordem, quantidade, setor, usuario="", campo_pendente="QUANTIDADE_PENDENTE", organizar=True):
    quantidade = float(quantidade)
    if quantidade <= 0:
        raise ValueError("Informe uma quantidade maior que zero.")

    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_setor_ordem(ordem, setor)
        if ultima_acao != "INICIO":
            if ultima_acao == "PAUSA":
                raise ValueError(f"Retome a etapa de {str(setor).lower()} antes de concluir.")
            raise ValueError(f"Inicie a etapa de {str(setor).lower()} antes de concluir.")

        pendente = float(ordem.get(campo_pendente, 0) or 0)
        if quantidade > pendente:
            raise ValueError(f"A quantidade passa do pendente de {str(setor).lower()} ({_formatar_numero(pendente)}).")

        acao = acao_descritiva("Fim" if quantidade >= pendente else "Parcial", setor)
        registrar_historico(ordem, quantidade, acao, avaliador=usuario, usuario_responsavel=usuario, organizar=organizar)
    carregar_historico.clear()


def lancar_inicio_qualidade(ordem, usuario):
    lancar_inicio_setor(ordem, "Qualidade", usuario=usuario)


def lancar_pausa_qualidade(ordem, usuario=""):
    lancar_pausa_setor(ordem, "Qualidade", usuario=usuario)


def lancar_inicio_embalagem(ordem, usuario=""):
    lancar_inicio_setor(ordem, "Embalagem", usuario=usuario)


def lancar_pausa_embalagem(ordem, usuario=""):
    lancar_pausa_setor(ordem, "Embalagem", usuario=usuario)


def lancar_conclusao_embalagem(ordem, quantidade, usuario=""):
    quantidade = float(quantidade)
    with _SHEETS_LOCK:
        usuario_inicio = ultimo_inicio_ativo_setor_ordem(ordem, "Embalagem")
        if not usuario_inicio:
            raise ValueError("Nao foi possivel identificar o usuario que iniciou a embalagem. Inicie a etapa novamente.")
        pendente = float(ordem.get("QUANTIDADE_PENDENTE", 0) or 0)
        lancar_movimento_setor(ordem, quantidade, "Embalagem", usuario=usuario_inicio, organizar=False)
        if quantidade < pendente:
            registrar_historico(
                ordem,
                0,
                acao_descritiva("Fim", "Embalagem"),
                avaliador=usuario_inicio,
                usuario_responsavel=usuario_inicio,
                organizar=False,
            )
        organizar_historico()


def lancar_aprovacao_qualidade(ordem, quantidade_aprovada, avaliador="", embalagem=False):
    quantidade_aprovada = float(quantidade_aprovada)
    if quantidade_aprovada <= 0:
        raise ValueError("Informe uma quantidade maior que zero.")

    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_setor_ordem(ordem, "Qualidade")
        if ultima_acao != "INICIO":
            if ultima_acao == "PAUSA":
                raise ValueError("Retome a etapa de qualidade antes de aprovar.")
            raise ValueError("Inicie a etapa de qualidade antes de aprovar.")
        usuario_inicio = ultimo_inicio_ativo_setor_ordem(ordem, "Qualidade")
        if not usuario_inicio:
            raise ValueError("Nao foi possivel identificar o usuario que iniciou a qualidade. Inicie a etapa novamente.")

        pendente = float(ordem.get("QUANTIDADE_PENDENTE", 0) or 0)
        if quantidade_aprovada > pendente:
            raise ValueError(f"A quantidade aprovada passa do pendente de qualidade ({_formatar_numero(pendente)}).")

        registros = [
            {
                "ordem": ordem,
                "quantidade": quantidade_aprovada,
                "acao": acao_descritiva("Aprovado", "Qualidade"),
                "avaliador": usuario_inicio,
                "usuario_responsavel": usuario_inicio,
            },
            {
                "ordem": ordem,
                "quantidade": 0,
                "acao": acao_descritiva("Fim", "Qualidade"),
                "avaliador": usuario_inicio,
                "usuario_responsavel": usuario_inicio,
            },
        ]
        if embalagem:
            registros.append({
                "ordem": ordem,
                "quantidade": quantidade_aprovada,
                "acao": acao_descritiva("Entrada", "Embalagem"),
                "avaliador": usuario_inicio,
                "usuario_responsavel": usuario_inicio,
            })
        registrar_historico_lote(registros)
    carregar_historico.clear()


def lancar_reprovacao_qualidade(ordem, quantidade_reprovada, avaliador=""):
    aba_origem = str(ordem["ABA_ORIGEM"])
    linha_planilha = int(ordem["LINHA_PLANILHA"])
    quantidade_reprovada = float(quantidade_reprovada)

    if quantidade_reprovada <= 0:
        raise ValueError("Informe uma quantidade maior que zero.")

    with _SHEETS_LOCK:
        ultima_acao = ultima_acao_setor_ordem(ordem, "Qualidade")
        if ultima_acao != "INICIO":
            if ultima_acao == "PAUSA":
                raise ValueError("Retome a etapa de qualidade antes de reprovar.")
            raise ValueError("Inicie a etapa de qualidade antes de reprovar.")
        usuario_inicio = ultimo_inicio_ativo_setor_ordem(ordem, "Qualidade")
        if not usuario_inicio:
            raise ValueError("Nao foi possivel identificar o usuario que iniciou a qualidade. Inicie a etapa novamente.")

        worksheet = abrir_planilha().worksheet(aba_origem)
        headers = worksheet.row_values(1)
        _confirmar_linha_ordem(worksheet, headers, linha_planilha, ordem)
        coluna_realizado = _indice_coluna(headers, "REALIZADO")
        realizado_atual = _numero_celula(worksheet.cell(linha_planilha, coluna_realizado).value)

        if quantidade_reprovada > realizado_atual:
            raise ValueError(f"A quantidade reprovada passa do realizado atual ({_formatar_numero(realizado_atual)}).")

        novo_realizado = max(realizado_atual - quantidade_reprovada, 0)
        worksheet.update_cell(linha_planilha, coluna_realizado, _formatar_numero(novo_realizado))
        try:
            ajustar_historico_reprovacao(ordem, quantidade_reprovada)
            registrar_historico_lote([
                {
                    "ordem": ordem,
                    "quantidade": quantidade_reprovada,
                    "acao": acao_descritiva("Reprovado", "Qualidade"),
                    "avaliador": usuario_inicio,
                    "usuario_responsavel": usuario_inicio,
                },
                {
                    "ordem": ordem,
                    "quantidade": 0,
                    "acao": acao_descritiva("Fim", "Qualidade"),
                    "avaliador": usuario_inicio,
                    "usuario_responsavel": usuario_inicio,
                },
            ])
        except Exception as exc:
            try:
                worksheet.update_cell(linha_planilha, coluna_realizado, _formatar_numero(realizado_atual))
                carregar_ordens.clear()
            except Exception:
                pass
            raise RuntimeError("A reprovacao foi desfeita porque nao foi possivel registrar o historico. Tente novamente.") from exc

    carregar_ordens.clear()
    carregar_historico.clear()


def ajustar_historico_reprovacao(ordem, quantidade_reprovada):
    with _SHEETS_LOCK:
        return _ajustar_historico_reprovacao_impl(ordem, quantidade_reprovada)


def _ajustar_historico_reprovacao_impl(ordem, quantidade_reprovada):
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    values = worksheet.get_all_values()
    if len(values) < 2:
        raise ValueError("Nao ha historico produtivo para ajustar.")

    headers = [str(coluna).strip() for coluna in values[0]]
    col_usuario = _indice_coluna_opcional(headers, ["USU\u00c1RIO RESPONSAVEL", "USUARIO RESPONSAVEL"])
    col_op = _indice_coluna_opcional(headers, ["N\u00b0 DA OP", "N DA OP", "OP"])
    col_codigo = _indice_coluna_opcional(headers, ["CODIGO"])
    col_produto = _indice_coluna_opcional(headers, ["PRODUTO"])
    col_quantidade = _indice_coluna_opcional(headers, ["QUANTIDADE"])
    col_tipo = _indice_coluna_opcional(headers, ["TIPO"])
    col_acao = _indice_coluna_opcional(headers, ["A\u00c7\u00c3O", "ACAO"])

    if not all([col_usuario, col_op, col_codigo, col_produto, col_quantidade, col_tipo, col_acao]):
        raise ValueError("A aba Historico precisa ter usuario, OP, codigo, produto, quantidade, tipo e acao.")

    def valor_linha(row, coluna):
        indice = coluna - 1
        return str(row[indice]).strip() if indice < len(row) else ""

    chave_ordem = {
        "usuario": _normalizar(ordem.get("USUARIO_RESPONSAVEL", "")),
        "op": _normalizar(ordem.get("OP", "")),
        "codigo": _normalizar(ordem.get("COD_PRODUTO", "")),
        "produto": _normalizar(ordem.get("PRODUTO", "")),
        "tipo": _normalizar(ordem.get("ABA_ORIGEM", "")),
    }

    linhas_produtivas = []
    for row_index, row in enumerate(values[1:], start=2):
        acao = valor_linha(row, col_acao)
        if not acao_produtiva_historico(acao):
            continue

        if (
            _normalizar(valor_linha(row, col_usuario)) != chave_ordem["usuario"]
            or _normalizar(valor_linha(row, col_op)) != chave_ordem["op"]
            or _normalizar(valor_linha(row, col_codigo)) != chave_ordem["codigo"]
            or _normalizar(valor_linha(row, col_produto)) != chave_ordem["produto"]
            or _normalizar(valor_linha(row, col_tipo)) != chave_ordem["tipo"]
        ):
            continue

        quantidade = _numero_celula(valor_linha(row, col_quantidade))
        if quantidade > 0:
            linhas_produtivas.append({
                "row": row_index,
                "acao": acao,
                "quantidade": quantidade,
            })

    total_produtivo = sum(linha["quantidade"] for linha in linhas_produtivas)
    if quantidade_reprovada > total_produtivo:
        raise ValueError(f"A quantidade reprovada passa do historico produtivo atual ({_formatar_numero(total_produtivo)}).")

    restante = float(quantidade_reprovada)
    atualizacoes = []
    linhas_ajustadas = []
    for linha in reversed(linhas_produtivas):
        if restante <= 0:
            break

        abatimento = min(linha["quantidade"], restante)
        nova_quantidade = linha["quantidade"] - abatimento
        restante -= abatimento
        linhas_ajustadas.append({**linha, "nova_quantidade": nova_quantidade})
        atualizacoes.append({
            "range": rowcol_to_a1(linha["row"], col_quantidade),
            "values": [[_formatar_numero(nova_quantidade)]],
        })

    total_apos_ajuste = total_produtivo - float(quantidade_reprovada)
    quantidade_ordem = float(ordem.get("QUANTIDADE_NUM", 0) or 0)
    if total_apos_ajuste < quantidade_ordem:
        for linha in linhas_ajustadas:
            if acao_base_historico(linha["acao"]) == "FIM" and linha["nova_quantidade"] > 0:
                atualizacoes.append({
                    "range": rowcol_to_a1(linha["row"], col_acao),
                    "values": [[acao_descritiva("Parcial", ordem.get("ABA_ORIGEM", ""))]],
                })

    if atualizacoes:
        worksheet.batch_update(atualizacoes, value_input_option="RAW")
    carregar_historico.clear()


def ultima_acao_controle_ordem(ordem):
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    values = worksheet.get_all_values()
    if len(values) < 2:
        return ""

    headers = [str(coluna).strip() for coluna in values[0]]
    col_usuario = _indice_coluna_opcional(headers, ["USU\u00c1RIO RESPONSAVEL", "USUARIO RESPONSAVEL"])
    col_op = _indice_coluna_opcional(headers, ["N\u00b0 DA OP", "N DA OP", "OP"])
    col_codigo = _indice_coluna_opcional(headers, ["CODIGO"])
    col_produto = _indice_coluna_opcional(headers, ["PRODUTO"])
    col_tipo = _indice_coluna_opcional(headers, ["TIPO"])
    col_acao = _indice_coluna_opcional(headers, ["A\u00c7\u00c3O", "ACAO"])

    if not all([col_usuario, col_op, col_codigo, col_produto, col_tipo, col_acao]):
        return ""

    def valor_linha(row, coluna):
        indice = coluna - 1
        return str(row[indice]).strip() if indice < len(row) else ""

    chave_ordem = {
        "usuario": _normalizar(ordem.get("USUARIO_RESPONSAVEL", "")),
        "op": _normalizar(ordem.get("OP", "")),
        "codigo": _normalizar(ordem.get("COD_PRODUTO", "")),
        "produto": _normalizar(ordem.get("PRODUTO", "")),
        "tipo": _normalizar(ordem.get("ABA_ORIGEM", "")),
    }

    ultima_acao = ""
    for row in values[1:]:
        acao = valor_linha(row, col_acao)
        acao_base = acao_base_historico(acao)
        if acao_base not in ["INICIO", "PAUSA", "FIM", "REPROVADO"]:
            continue
        etapa_controle = acao_etapa_historico(acao)
        if acao_base == "REPROVADO":
            etapa_controle = chave_ordem["tipo"]
        if etapa_controle != chave_ordem["tipo"]:
            continue

        if (
            _normalizar(valor_linha(row, col_usuario)) != chave_ordem["usuario"]
            or _normalizar(valor_linha(row, col_op)) != chave_ordem["op"]
            or _normalizar(valor_linha(row, col_codigo)) != chave_ordem["codigo"]
            or _normalizar(valor_linha(row, col_produto)) != chave_ordem["produto"]
            or _normalizar(valor_linha(row, col_tipo)) != chave_ordem["tipo"]
        ):
            continue

        ultima_acao = acao_base

    return ultima_acao


def ultima_acao_setor_ordem(ordem, setor):
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    values = worksheet.get_all_values()
    if len(values) < 2:
        return ""

    headers = [str(coluna).strip() for coluna in values[0]]
    col_usuario = _indice_coluna_opcional(headers, ["USU\u00c1RIO RESPONSAVEL", "USUARIO RESPONSAVEL"])
    col_op = _indice_coluna_opcional(headers, ["N\u00b0 DA OP", "N DA OP", "OP"])
    col_codigo = _indice_coluna_opcional(headers, ["CODIGO"])
    col_produto = _indice_coluna_opcional(headers, ["PRODUTO"])
    col_tipo = _indice_coluna_opcional(headers, ["TIPO"])
    col_acao = _indice_coluna_opcional(headers, ["A\u00c7\u00c3O", "ACAO"])

    if not all([col_usuario, col_op, col_codigo, col_produto, col_tipo, col_acao]):
        return ""

    def valor_linha(row, coluna):
        indice = coluna - 1
        return str(row[indice]).strip() if indice < len(row) else ""

    chave_ordem = {
        "usuario": _normalizar(ordem.get("USUARIO_RESPONSAVEL", "")),
        "op": _normalizar(ordem.get("OP", "")),
        "codigo": _normalizar(ordem.get("COD_PRODUTO", "")),
        "produto": _normalizar(ordem.get("PRODUTO", "")),
        "tipo": _normalizar(ordem.get("ABA_ORIGEM", "")),
    }

    setor_norm = _normalizar(setor)
    ultima_acao = ""
    for row in values[1:]:
        acao = valor_linha(row, col_acao)
        acao_base = acao_base_historico(acao)
        acao_etapa = acao_etapa_historico(acao)
        if acao_base not in ["INICIO", "PAUSA", "FIM"] or acao_etapa != setor_norm:
            continue

        if (
            _normalizar(valor_linha(row, col_op)) != chave_ordem["op"]
            or _normalizar(valor_linha(row, col_codigo)) != chave_ordem["codigo"]
            or _normalizar(valor_linha(row, col_produto)) != chave_ordem["produto"]
            or _normalizar(valor_linha(row, col_tipo)) != chave_ordem["tipo"]
        ):
            continue

        ultima_acao = acao_base

    return ultima_acao


def ultimo_inicio_ativo_setor_ordem(ordem, setor):
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    values = worksheet.get_all_values()
    if len(values) < 2:
        return ""

    headers = [str(coluna).strip() for coluna in values[0]]
    col_usuario = _indice_coluna_opcional(headers, ["USU\u00c1RIO RESPONSAVEL", "USUARIO RESPONSAVEL"])
    col_op = _indice_coluna_opcional(headers, ["N\u00b0 DA OP", "N DA OP", "OP"])
    col_codigo = _indice_coluna_opcional(headers, ["CODIGO"])
    col_produto = _indice_coluna_opcional(headers, ["PRODUTO"])
    col_tipo = _indice_coluna_opcional(headers, ["TIPO"])
    col_acao = _indice_coluna_opcional(headers, ["A\u00c7\u00c3O", "ACAO"])

    if not all([col_usuario, col_op, col_codigo, col_produto, col_tipo, col_acao]):
        return ""

    def valor_linha(row, coluna):
        indice = coluna - 1
        return str(row[indice]).strip() if indice < len(row) else ""

    chave_ordem = {
        "op": _normalizar(ordem.get("OP", "")),
        "codigo": _normalizar(ordem.get("COD_PRODUTO", "")),
        "produto": _normalizar(ordem.get("PRODUTO", "")),
        "tipo": _normalizar(ordem.get("ABA_ORIGEM", "")),
    }

    setor_norm = _normalizar(setor)
    usuario_inicio = ""
    ultima_acao = ""
    for row in values[1:]:
        acao = valor_linha(row, col_acao)
        acao_base = acao_base_historico(acao)
        acao_etapa = acao_etapa_historico(acao)
        if acao_base not in ["INICIO", "PAUSA", "FIM"] or acao_etapa != setor_norm:
            continue

        if (
            _normalizar(valor_linha(row, col_op)) != chave_ordem["op"]
            or _normalizar(valor_linha(row, col_codigo)) != chave_ordem["codigo"]
            or _normalizar(valor_linha(row, col_produto)) != chave_ordem["produto"]
            or _normalizar(valor_linha(row, col_tipo)) != chave_ordem["tipo"]
        ):
            continue

        ultima_acao = acao_base
        usuario_inicio = valor_linha(row, col_usuario) if acao_base == "INICIO" else ""

    return usuario_inicio if ultima_acao == "INICIO" else ""


def ultima_acao_embalagem_ordem(ordem):
    ultima_acao = ultima_acao_setor_ordem(ordem, "Embalagem")
    return f"{ultima_acao} EMBALAGEM" if ultima_acao else ""


def registrar_historico(ordem, quantidade_lancada, acao, avaliador="", usuario_responsavel="", organizar=True):
    with _SHEETS_LOCK:
        worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
        headers = worksheet.row_values(1)
        linha = _montar_linha_historico(headers, ordem, quantidade_lancada, acao, avaliador, usuario_responsavel)

        worksheet.append_row(linha, value_input_option="RAW")
        if organizar:
            organizar_historico()
    carregar_historico.clear()


def registrar_historico_lote(registros, organizar=True):
    registros = [registro for registro in registros if registro]
    if not registros:
        return

    with _SHEETS_LOCK:
        worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
        headers = worksheet.row_values(1)
        linhas = [
            _montar_linha_historico(
                headers,
                registro.get("ordem", {}),
                registro.get("quantidade", 0),
                registro.get("acao", ""),
                registro.get("avaliador", ""),
                registro.get("usuario_responsavel", ""),
            )
            for registro in registros
        ]

        worksheet.append_rows(linhas, value_input_option="RAW")
        if organizar:
            organizar_historico()
    carregar_historico.clear()


def _montar_linha_historico(headers, ordem, quantidade_lancada, acao, avaliador="", usuario_responsavel=""):
    data_hora = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M:%S")
    linha = []

    for header in headers:
        header_normalizado = _normalizar(header)
        if header_normalizado == _normalizar("USU\u00c1RIO RESPONSAVEL"):
            linha.append(str(usuario_responsavel or ordem.get("USUARIO_RESPONSAVEL", "")))
        elif header_normalizado == _normalizar("N\u00b0 DA OP"):
            linha.append(str(ordem.get("OP", "")))
        elif header_normalizado == _normalizar("DATA / HORA"):
            linha.append(data_hora)
        elif header_normalizado == "CODIGO":
            linha.append(str(ordem.get("COD_PRODUTO", "")))
        elif header_normalizado == "PRODUTO":
            linha.append(str(ordem.get("PRODUTO", "")))
        elif header_normalizado == "QUANTIDADE":
            linha.append(_formatar_numero(quantidade_lancada))
        elif header_normalizado == "TIPO":
            linha.append(str(ordem.get("ABA_ORIGEM", "")))
        elif header_normalizado == "ACAO":
            linha.append(str(acao))
        elif header_normalizado in ["AVALIADOR", "QUALIDADE", "RESPONSAVELQUALIDADE", "USUARIOQUALIDADE"]:
            linha.append(str(avaliador))
        elif header_normalizado in ["OBS", "OBSERVACAO", "OBSERVACOES"] and avaliador:
            linha.append(f"Avaliador: {avaliador}")
        else:
            linha.append("")

    return linha


def organizar_historico():
    with _SHEETS_LOCK:
        _organizar_historico_impl()


def _organizar_historico_impl():
    worksheet = abrir_planilha().worksheet(ABA_HISTORICO)
    values = worksheet.get_all_values()
    if len(values) < 3:
        return

    headers = [str(coluna).strip() for coluna in values[0]]
    col_op = _indice_coluna_opcional(headers, ["N\u00b0 DA OP", "N DA OP", "OP"])
    col_data = _indice_coluna_opcional(headers, ["DATA / HORA", "DATA HORA"])
    col_codigo = _indice_coluna_opcional(headers, ["CODIGO"])
    col_produto = _indice_coluna_opcional(headers, ["PRODUTO"])
    col_tipo = _indice_coluna_opcional(headers, ["TIPO"])
    if not all([col_op, col_data, col_codigo, col_produto, col_tipo]):
        return

    def valor_linha(row, coluna):
        indice = coluna - 1
        return str(row[indice]).strip() if indice < len(row) else ""

    linhas = []
    largura = len(headers)
    for posicao, row in enumerate(values[1:]):
        row = [str(valor).strip() for valor in row]
        if not any(row):
            continue
        row = row[:largura] + [""] * max(0, largura - len(row))
        data_hora = pd.to_datetime(valor_linha(row, col_data), dayfirst=True, errors="coerce")
        if pd.isna(data_hora):
            data_hora = pd.Timestamp.max
        linhas.append(
            {
                "row": row,
                "tipo": _normalizar(valor_linha(row, col_tipo)),
                "op": _normalizar(valor_linha(row, col_op)),
                "codigo": _normalizar(valor_linha(row, col_codigo)),
                "produto": _normalizar(valor_linha(row, col_produto)),
                "data_hora": data_hora,
                "posicao": posicao,
            }
        )

    if not linhas:
        worksheet.batch_clear(["A2:ZZ"])
        return

    linhas_ordenadas = sorted(
        linhas,
        key=lambda item: (
            item["tipo"],
            item["op"],
            item["codigo"],
            item["produto"],
            item["data_hora"],
            item["posicao"],
        ),
    )
    valores_ordenados = [item["row"] for item in linhas_ordenadas]
    worksheet.batch_clear(["A2:ZZ"])
    worksheet.update("A2", valores_ordenados, value_input_option="RAW")


def _limpar_dataframe(df):
    df = df.copy()
    df.columns = [str(coluna).strip() for coluna in df.columns]
    df = df.dropna(how="all")
    df = df.loc[:, [coluna for coluna in df.columns if str(coluna).strip()]]

    for coluna in df.columns:
        df[coluna] = df[coluna].fillna("").astype(str).str.strip()

    return df


def _garantir_colunas(df, colunas):
    df = df.copy()
    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = pd.Series(dtype=_dtype_coluna(coluna))
    return df


def _dtype_coluna(coluna):
    if coluna in ["QUANTIDADE_NUM", "REALIZADO_NUM", "SALDO_NUM", "DIAS_ATRASO"]:
        return "float64"
    if coluna in ["DATA_PRIORIDADE", "DATA_HORA_DT", "DATA"]:
        return "datetime64[ns]"
    if coluna == "ATRASADA":
        return "bool"
    return "object"


def _ordens_vazias():
    return pd.DataFrame({
        coluna: pd.Series(dtype=_dtype_coluna(coluna))
        for coluna in COLUNAS_ORDENS
    })


def _historico_vazio():
    return pd.DataFrame({
        coluna: pd.Series(dtype=_dtype_coluna(coluna))
        for coluna in COLUNAS_HISTORICO
    })


def _produtos_vazios():
    return pd.DataFrame({
        coluna: pd.Series(dtype="object")
        for coluna in COLUNAS_PRODUTOS
    })


def _padronizar_usuarios(df):
    df = df.copy()
    colunas = {
        "Codigo": _encontrar_coluna(df, ["CODIGO", "CODIGO USUARIO", "COD"]),
        "Nome": _encontrar_coluna(df, ["NOME", "USUARIO", "USU\u00c1RIO"]),
        "Cargo": _encontrar_coluna(df, ["CARGO", "FUNCAO", "FUN\u00c7\u00c3O"]),
    }

    usuarios = pd.DataFrame()
    for nome_padrao, coluna_origem in colunas.items():
        if coluna_origem is None:
            usuarios[nome_padrao] = pd.Series(dtype="object")
        else:
            usuarios[nome_padrao] = df[coluna_origem].astype(str).str.strip()

    return _garantir_colunas(usuarios, COLUNAS_USUARIOS)


def _feriados_vazios():
    return pd.DataFrame({
        "DATA": pd.Series(dtype="datetime64[ns]")
    })


def _padronizar_produtos(df):
    df = df.copy()
    colunas = {
        "COD_PRODUTO": _encontrar_coluna(df, ["COD_PRODUTO", "CODIGO PRODUTO", "CODIGO", "COD", "SKU", "COD ITEM"]),
        "PRODUTO": _encontrar_coluna(df, ["PRODUTO", "DESCRI\u00c7\u00c3O", "DESCRICAO", "ITEM", "DESCRI\u00c7\u00c3O ITEM", "DESCRICAO ITEM"]),
        "CATEGORIA": _encontrar_coluna(df, ["CATEGORIA", "CATEGORIA PRODUTO"]),
        "MARCA": _encontrar_coluna(df, ["MARCA", "BRAND"]),
        "GRUPO": _encontrar_coluna(df, ["GRUPO", "GRUPO PRODUTO", "FAM\u00cdLIA", "FAMILIA"]),
    }

    produtos = pd.DataFrame()
    for nome_padrao, coluna_origem in colunas.items():
        if coluna_origem is None:
            produtos[nome_padrao] = pd.Series(dtype="object")
        else:
            produtos[nome_padrao] = df[coluna_origem].astype(str).str.strip()

    campos_chave = ["COD_PRODUTO", "PRODUTO", "CATEGORIA", "MARCA", "GRUPO"]
    tem_dados = produtos[campos_chave].apply(lambda linha: any(str(valor).strip() for valor in linha), axis=1)
    produtos = produtos[tem_dados].copy()
    if produtos.empty:
        return _produtos_vazios()

    produtos = produtos.drop_duplicates(subset=["COD_PRODUTO", "PRODUTO"], keep="first")
    return _garantir_colunas(produtos, COLUNAS_PRODUTOS)


def _remover_linhas_de_cabecalho_repetido(df):
    if df.empty:
        return df

    primeira_coluna = next(
        (coluna for coluna in df.columns if coluna not in ["ABA_ORIGEM", "LINHA_PLANILHA"]),
        df.columns[0],
    )
    return df[df[primeira_coluna].astype(str).str.strip() != primeira_coluna].copy()


def _montar_linha_planejamento(aba, headers, dados):
    def valor_texto(chaves, padrao=""):
        for chave in chaves:
            valor = dados.get(chave, "")
            if str(valor).strip():
                return str(valor).strip()
        return padrao

    mapa = {
        "DATAABERTURA": _formatar_data_planilha(dados.get("DATA_ABERTURA")),
        "DATA": _formatar_data_planilha(dados.get("DATA")),
        "NDAOP": valor_texto(["OP"]),
        "OP": valor_texto(["OP"]),
        "CODPRODUTO": valor_texto(["COD_PRODUTO"]),
        "CODIGOPRODUTO": valor_texto(["COD_PRODUTO"]),
        "DESCRICAO": valor_texto(["PRODUTO"]),
        "CODPECA": valor_texto(["COD_PECA"]),
        "DESCRICAOPECA": valor_texto(["PECA"]),
        "QTDPECAS": valor_texto(["QTD_PECAS"]),
        "QUANTIDADE": valor_texto(["QUANTIDADE"]),
        "OBS": valor_texto(["OBS"]),
        "DATAPREVISTA": _formatar_data_planilha(dados.get("DATA_PREVISTA")),
        "REALIZADO": "",
        "STATUS": "PENDENTE",
        "USUARIORESPONSAVEL": valor_texto(["USUARIO_RESPONSAVEL"]),
    }

    linha = []
    for header in headers:
        linha.append(mapa.get(_normalizar(header), ""))
    return linha


def _data_bloco_ordem(aba, dados):
    if aba == ABAS_PLANEJAMENTO[0]:
        return pd.to_datetime(dados.get("DATA_PREVISTA") or dados.get("DATA_ABERTURA"), dayfirst=True, errors="coerce")
    return pd.to_datetime(dados.get("DATA"), dayfirst=True, errors="coerce")


def _formatar_data_planilha(valor):
    data = pd.to_datetime(valor, dayfirst=True, errors="coerce")
    if pd.isna(data):
        return ""
    return data.strftime("%d/%m/%Y")


def _semana_data(valor):
    data = pd.to_datetime(valor, dayfirst=True, errors="coerce")
    if pd.isna(data):
        return None
    data = data.normalize()
    return data - pd.Timedelta(days=int(data.weekday()))


def _localizar_insercao_planejamento(values, headers, data_bloco):
    if not values:
        return {"linha": 1, "novo_bloco": True}

    largura = len(headers)
    headers_norm = [_normalizar(header) for header in headers]
    header_rows = []
    for indice, row in enumerate(values, start=1):
        row_norm = [_normalizar(valor) for valor in row[:largura]]
        if row_norm[: len(headers_norm)] == headers_norm:
            header_rows.append(indice)

    semana_alvo = _semana_data(data_bloco)
    if semana_alvo is not None:
        for posicao, linha_header in enumerate(header_rows):
            inicio = linha_header + 1
            fim = (header_rows[posicao + 1] - 1) if posicao + 1 < len(header_rows) else len(values)
            if _bloco_tem_semana(values, inicio, fim, headers, semana_alvo):
                return {"linha": fim + 1, "novo_bloco": False}

    ultima_linha = _ultima_linha_usada(values)
    return {"linha": ultima_linha + 1, "novo_bloco": True}


def _bloco_tem_semana(values, inicio, fim, headers, semana_alvo):
    coluna_data = _indice_data_bloco(headers)
    if coluna_data is None:
        return False
    for row in values[inicio - 1:fim]:
        if coluna_data >= len(row):
            continue
        semana = _semana_data(row[coluna_data])
        if semana is not None and semana == semana_alvo:
            return True
    return False


def _indice_data_bloco(headers):
    candidatos = ["DATAPREVISTA", "DATA", "DATAABERTURA"]
    for candidato in candidatos:
        for indice, header in enumerate(headers):
            if _normalizar(header) == candidato:
                return indice
    return None


def _ultima_linha_usada(values):
    for indice in range(len(values), 0, -1):
        if any(str(valor).strip() for valor in values[indice - 1]):
            return indice
    return 0


def _copiar_formatos_planejamento(worksheet, linha_inserida, largura, novo_bloco):
    sheet_id = worksheet.id
    requests = []
    if novo_bloco:
        requests.append(_request_copiar_formato(sheet_id, 1, linha_inserida, largura))
        requests.append(_request_copiar_formato(sheet_id, 2, linha_inserida + 1, largura))
        requests.append(_request_copiar_formato(sheet_id, 3, linha_inserida + 2, largura))
        requests.append(_request_altura_linha(sheet_id, linha_inserida + 2, 15))
    else:
        requests.append(_request_copiar_formato(sheet_id, 2, linha_inserida, largura))
        requests.append(_request_copiar_formato(sheet_id, 3, linha_inserida + 1, largura))
        requests.append(_request_altura_linha(sheet_id, linha_inserida + 1, 15))
    if requests:
        abrir_planilha().batch_update({"requests": requests})


def _request_copiar_formato(sheet_id, linha_origem, linha_destino, largura):
    return {
        "copyPaste": {
            "source": {
                "sheetId": sheet_id,
                "startRowIndex": linha_origem - 1,
                "endRowIndex": linha_origem,
                "startColumnIndex": 0,
                "endColumnIndex": largura,
            },
            "destination": {
                "sheetId": sheet_id,
                "startRowIndex": linha_destino - 1,
                "endRowIndex": linha_destino,
                "startColumnIndex": 0,
                "endColumnIndex": largura,
            },
            "pasteType": "PASTE_FORMAT",
            "pasteOrientation": "NORMAL",
        }
    }


def _request_altura_linha(sheet_id, linha, altura_pixels):
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": linha - 1,
                "endIndex": linha,
            },
            "properties": {
                "pixelSize": altura_pixels,
            },
            "fields": "pixelSize",
        }
    }


def _padronizar_ordens(df):
    df = df.copy()
    colunas = {
        "USUARIO_RESPONSAVEL": _encontrar_coluna(df, ["USU\u00c1RIO RESPONSAVEL", "USUARIO RESPONSAVEL"]),
        "STATUS": _encontrar_coluna(df, ["STATUS"]),
        "OP": _encontrar_coluna(df, ["N\u00b0 DA OP", "N DA OP", "OP"]),
        "COD_PRODUTO": _encontrar_coluna(df, ["COD_PRODUTO", "CODIGO PRODUTO"]),
        "PRODUTO": _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O", "DESCRICAO"]),
        "COD_PECA": _encontrar_coluna(df, ["COD_PE\u00c7A", "COD_PECA"]),
        "PECA": _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O PE\u00c7A", "DESCRICAO PECA"]),
        "QTD_PECAS": _encontrar_coluna(df, ["QTD_PE\u00c7AS", "QTD_PECAS"]),
        "QUANTIDADE": _encontrar_coluna(df, ["QUANTIDADE"]),
        "REALIZADO": _encontrar_coluna(df, ["REALIZADO"]),
        "DATA_ABERTURA": _encontrar_coluna(df, ["DATA_ABERTURA"]),
        "DATA_PREVISTA": _encontrar_coluna(df, ["DATA_PREVISTA"]),
        "DATA": _encontrar_coluna(df, ["DATA"]),
        "OBS": _encontrar_coluna(df, ["OBS", "A\u00c7\u00c3O", "ACAO"]),
    }

    for nome_padrao, coluna_origem in colunas.items():
        if coluna_origem is None:
            df[nome_padrao] = ""
        else:
            df[nome_padrao] = df[coluna_origem].astype(str).str.strip()

    campos_chave = ["OP", "COD_PRODUTO", "PRODUTO", "QUANTIDADE", "REALIZADO", "STATUS", "DATA", "DATA_PREVISTA", "OBS"]
    tem_dados = df[campos_chave].apply(lambda linha: any(str(valor).strip() for valor in linha), axis=1)
    df = df[tem_dados].copy()

    if df.empty:
        return _garantir_colunas(df, COLUNAS_ORDENS)

    df["USUARIO_RESPONSAVEL"] = df["USUARIO_RESPONSAVEL"].replace("", "Sem responsavel")
    df["STATUS"] = df["STATUS"].replace("", "Sem status")
    df["REALIZADO"] = df["REALIZADO"].replace("", "0")
    df["QUANTIDADE_NUM"] = _serie_numero(df["QUANTIDADE"])
    df["REALIZADO_NUM"] = _serie_numero(df["REALIZADO"])
    df["SALDO_NUM"] = (df["QUANTIDADE_NUM"] - df["REALIZADO_NUM"]).clip(lower=0)
    df["DATA_PRIORIDADE"] = pd.to_datetime(df.apply(_data_prioridade, axis=1), errors="coerce")
    df["DIAS_ATRASO"] = (pd.Timestamp.today().normalize() - df["DATA_PRIORIDADE"]).dt.days
    df["ATRASADA"] = (df["DIAS_ATRASO"] > 0) & (df["STATUS"].str.upper() != "OK")

    return _garantir_colunas(df, COLUNAS_ORDENS)


def _vincular_pecas_a_ordem(df):
    if df.empty:
        return df

    df = df.copy()
    coluna_op = _encontrar_coluna(df, ["N\u00b0 DA OP", "N DA OP", "OP"])
    coluna_cod_produto = _encontrar_coluna(df, ["COD_PRODUTO", "CODIGO PRODUTO"])
    coluna_produto = _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O", "DESCRICAO"])
    coluna_cod_peca = _encontrar_coluna(df, ["COD_PE\u00c7A", "COD_PECA"])
    coluna_peca = _encontrar_coluna(df, ["DESCRI\u00c7\u00c3O PE\u00c7A", "DESCRICAO PECA"])
    coluna_qtd_pecas = _encontrar_coluna(df, ["QTD_PE\u00c7AS", "QTD_PECAS"])

    if not all([coluna_op, coluna_cod_produto, coluna_produto]):
        df["PECAS_BLOCO"] = [[] for _ in range(len(df))]
        return df

    pecas_por_linha_mae = {}
    linha_mae_atual = None

    for indice, linha in df.iterrows():
        tem_ordem = any(
            str(linha.get(coluna, "")).strip()
            for coluna in [coluna_op, coluna_cod_produto, coluna_produto]
        )

        if tem_ordem:
            linha_mae_atual = indice
            pecas_por_linha_mae.setdefault(indice, [])

        if linha_mae_atual is None:
            continue

        codigo_peca = str(linha.get(coluna_cod_peca, "")).strip() if coluna_cod_peca else ""
        descricao_peca = str(linha.get(coluna_peca, "")).strip() if coluna_peca else ""
        qtd_pecas = str(linha.get(coluna_qtd_pecas, "")).strip() if coluna_qtd_pecas else ""

        if codigo_peca or descricao_peca or qtd_pecas:
            pecas_por_linha_mae.setdefault(linha_mae_atual, []).append(
                {
                    "Cod. peca": codigo_peca,
                    "Peca faltante": descricao_peca,
                    "Qtd. pecas": qtd_pecas,
                }
            )

    df["PECAS_BLOCO"] = [
        pecas_por_linha_mae.get(indice, [])
        for indice in df.index
    ]
    return df


def _data_prioridade(linha):
    if linha["ABA_ORIGEM"] == "Produ\u00e7\u00e3o":
        texto_data = linha.get("DATA_PREVISTA", "")
    else:
        texto_data = linha.get("DATA", "")

    data = pd.to_datetime(texto_data, dayfirst=True, errors="coerce")
    return data.normalize() if pd.notna(data) else pd.NaT


def _serie_numero(serie):
    return pd.to_numeric(
        serie.fillna("").astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    ).fillna(0)


def _numero_celula(valor):
    numero = pd.to_numeric(str(valor or "").strip().replace(",", "."), errors="coerce")
    return 0 if pd.isna(numero) else float(numero)


def _indice_coluna(headers, nome):
    nome_normalizado = _normalizar(nome)
    for index, header in enumerate(headers, start=1):
        if _normalizar(header) == nome_normalizado:
            return index
    raise ValueError(f"Coluna {nome} nao encontrada.")


def _indice_coluna_opcional(headers, nomes):
    mapa = {_normalizar(header): index for index, header in enumerate(headers, start=1)}
    for nome in nomes:
        indice = mapa.get(_normalizar(nome))
        if indice:
            return indice
    return None


def _confirmar_linha_ordem(worksheet, headers, linha_planilha, ordem):
    col_op = _indice_coluna_opcional(headers, ["N° DA OP", "N DA OP", "OP"])
    col_codigo = _indice_coluna_opcional(headers, ["COD_PRODUTO", "CODIGO PRODUTO", "CODIGO"])
    if not col_op or not col_codigo:
        return

    valores = worksheet.row_values(linha_planilha)

    def valor(coluna):
        indice = coluna - 1
        return str(valores[indice]).strip() if indice < len(valores) else ""

    op_confere = _normalizar(valor(col_op)) == _normalizar(ordem.get("OP", ""))
    codigo_confere = _normalizar(valor(col_codigo)) == _normalizar(ordem.get("COD_PRODUTO", ""))
    if not op_confere or not codigo_confere:
        carregar_ordens.clear()
        raise RuntimeError(
            "A programacao foi alterada por outra pessoa desde que esta pagina foi carregada. "
            "Atualize a pagina e tente novamente."
        )


def _encontrar_coluna(df, nomes):
    mapa = {_normalizar(coluna): coluna for coluna in df.columns}
    for nome in nomes:
        coluna = mapa.get(_normalizar(nome))
        if coluna:
            return coluna
    return None


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto).strip().upper())
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return "".join(char for char in texto if char.isalnum())


def _formatar_numero(valor):
    valor = float(valor)
    if valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")
