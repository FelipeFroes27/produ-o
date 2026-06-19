from datetime import time

import pandas as pd


JANELAS_TRABALHO_PADRAO = [
    ("Manha", time(8, 0), time(13, 0)),
    ("Tarde", time(14, 0), time(18, 0)),
]
JANELAS_TRABALHO_SEXTA = [
    ("Manha", time(8, 0), time(13, 0)),
    ("Tarde", time(14, 0), time(17, 0)),
]


def formatar_duracao_horas(horas):
    horas = max(float(horas or 0), 0)
    minutos_totais = int(round(horas * 60))
    dias = minutos_totais // (24 * 60)
    minutos_restantes = minutos_totais % (24 * 60)
    horas_restantes = minutos_restantes // 60
    minutos = minutos_restantes % 60

    partes = []
    if dias:
        partes.append(f"{dias} dia{'s' if dias != 1 else ''}")
    if horas_restantes or dias:
        partes.append(f"{horas_restantes} hora{'s' if horas_restantes != 1 else ''}")
    partes.append(f"{minutos} min")
    return " ".join(partes)


def montar_datas_feriados(feriados):
    if feriados is None or feriados.empty or "DATA" not in feriados.columns:
        return set()

    datas = pd.to_datetime(feriados["DATA"], dayfirst=True, errors="coerce").dropna()
    return {data.date() for data in datas}


def janelas_trabalho_do_dia(dia, feriados=None):
    feriados = feriados or set()
    data = dia.date()
    if dia.weekday() >= 5 or data in feriados:
        return []
    if dia.weekday() == 4:
        return JANELAS_TRABALHO_SEXTA
    return JANELAS_TRABALHO_PADRAO


def calcular_horas_comerciais(inicio, fim, feriados=None):
    return sum(item["HORAS"] for item in detalhar_horas_comerciais(inicio, fim, feriados))


def detalhar_horas_comerciais(inicio, fim, feriados=None):
    inicio = pd.to_datetime(inicio, errors="coerce")
    fim = pd.to_datetime(fim, errors="coerce")
    if pd.isna(inicio) or pd.isna(fim) or fim <= inicio:
        return []

    feriados = feriados or set()
    detalhes = []
    dia = inicio.normalize()
    ultimo_dia = fim.normalize()

    while dia <= ultimo_dia:
        data = dia.date()
        if data in feriados:
            detalhes.append(_linha_dia_nao_contado(dia, "Feriado"))
            dia += pd.Timedelta(days=1)
            continue
        if dia.weekday() >= 5:
            detalhes.append(_linha_dia_nao_contado(dia, "Fim de semana"))
            dia += pd.Timedelta(days=1)
            continue

        for periodo, hora_inicio, hora_fim in janelas_trabalho_do_dia(dia, feriados):
            janela_inicio = pd.Timestamp.combine(data, hora_inicio)
            janela_fim = pd.Timestamp.combine(data, hora_fim)
            inicio_util = max(inicio, janela_inicio)
            fim_util = min(fim, janela_fim)
            if fim_util > inicio_util:
                horas = (fim_util - inicio_util).total_seconds() / 3600
                detalhes.append({
                    "DATA": dia,
                    "DIA": dia.strftime("%d/%m/%Y"),
                    "PERIODO": periodo,
                    "INTERVALO": f"{inicio_util.strftime('%H:%M')} as {fim_util.strftime('%H:%M')}",
                    "HORAS": horas,
                    "TEMPO": formatar_duracao_horas(horas),
                    "OBS": "Tempo contado",
                    "CONTADO": True,
                })

        dia += pd.Timedelta(days=1)

    return detalhes


def _linha_dia_nao_contado(dia, motivo):
    return {
        "DATA": dia,
        "DIA": dia.strftime("%d/%m/%Y"),
        "PERIODO": motivo,
        "INTERVALO": "Dia inteiro",
        "HORAS": 0.0,
        "TEMPO": "0 min",
        "OBS": "Nao entra no leadtime",
        "CONTADO": False,
    }
