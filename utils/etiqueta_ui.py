"""Janela da etiqueta de produção: depois de finalizar uma etapa com a caixinha
"Etiqueta" marcada, a página pede as etiquetas (`solicitar_etiquetas`) e, na
execução seguinte, `mostrar_etiquetas_pendentes` abre a janela com a prévia e o
download do PDF. As etiquetas são geradas em memória e não ficam salvas."""
import uuid
from datetime import datetime, timedelta, timezone

import streamlit as st

from utils.label import formatar_ordem, gerar_etiquetas

PENDENTE = "etiqueta_pendente"
FUSO_BRASILIA = timezone(timedelta(hours=-3))


@st.cache_resource
def _etiquetas_geradas():
    # chave da finalização -> quando a etiqueta foi gerada; vale para todos os
    # usuários enquanto o app estiver no ar (não é gravado em lugar nenhum)
    return {}


def solicitar_etiquetas(codigo, descricao, itens, chave):
    """Pede a janela da etiqueta para a próxima execução da página.

    `itens` = [{"ordem", "responsavel", "unidades"}] (uma etiqueta por unidade);
    `chave` identifica a finalização, para avisar se ela já teve etiqueta gerada."""
    for nome in [nome for nome in st.session_state if str(nome).startswith(("etiqueta_resultado_", "etiqueta_regerar_"))]:
        st.session_state.pop(nome, None)
    st.session_state[PENDENTE] = {
        "id": uuid.uuid4().hex,
        "codigo": str(codigo),
        "descricao": str(descricao),
        "itens": [dict(item) for item in itens],
        "chave": str(chave),
    }


def mostrar_etiquetas_pendentes():
    pedido = st.session_state.pop(PENDENTE, None)
    if pedido:
        # um problema na etiqueta nunca pode impedir a página de abrir
        try:
            _dialog_etiquetas(pedido)
        except Exception:
            st.warning("Não foi possível abrir a janela da etiqueta.")


@st.dialog("Etiqueta de produção", width="large")
def _dialog_etiquetas(pedido):
    chave_resultado = f"etiqueta_resultado_{pedido['id']}"
    chave_regerar = f"etiqueta_regerar_{pedido['id']}"
    geradas = _etiquetas_geradas()
    resultado = st.session_state.get(chave_resultado)

    if resultado is None:
        anterior = geradas.get(pedido["chave"])
        if anterior and not st.session_state.get(chave_regerar):
            st.warning(
                f"Já foi gerada uma etiqueta para esta mesma finalização em {anterior:%d/%m/%Y às %H:%M}. "
                "Deseja gerar de novo?"
            )
            col_gerar, col_cancelar = st.columns(2)
            col_gerar.button(
                "Gerar novamente",
                key=f"etiqueta_btn_regerar_{pedido['id']}",
                type="primary",
                use_container_width=True,
                on_click=lambda: st.session_state.__setitem__(chave_regerar, True),
            )
            if col_cancelar.button("Não gerar", key=f"etiqueta_btn_cancelar_{pedido['id']}", use_container_width=True):
                st.rerun()
            return
        try:
            with st.spinner("Gerando etiquetas..."):
                resultado = gerar_etiquetas(pedido["codigo"], pedido["descricao"], pedido["itens"])
        except Exception as exc:
            st.error(f"Não foi possível gerar a etiqueta: {exc}")
            return
        st.session_state[chave_resultado] = resultado
        geradas[pedido["chave"]] = datetime.now(FUSO_BRASILIA)

    pdf, png, total = resultado
    st.success(f"{total} etiqueta{'s' if total != 1 else ''} pronta{'s' if total != 1 else ''} (uma por unidade).")
    for item in pedido["itens"]:
        if int(item["unidades"]) > 0:
            st.caption(f"{formatar_ordem(item['ordem'])} · {str(item['responsavel']).upper()}: {int(item['unidades'])} etiqueta(s)")
    st.image(png, caption="Prévia da primeira etiqueta (100 x 60 mm)", width=520)

    nome_base = f"Etiquetas_{pedido['codigo']}_{datetime.now(FUSO_BRASILIA):%Y-%m-%d_%H-%M-%S}"
    col_pdf, col_png = st.columns([2, 1])
    col_pdf.download_button(
        "Baixar PDF para imprimir",
        data=pdf,
        file_name=f"{nome_base}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
        on_click="ignore",
        key=f"etiqueta_dl_pdf_{pedido['id']}",
    )
    col_png.download_button(
        "Baixar PNG",
        data=png,
        file_name=f"{nome_base}.png",
        mime="image/png",
        use_container_width=True,
        on_click="ignore",
        key=f"etiqueta_dl_png_{pedido['id']}",
    )
    st.caption("Imprima em tamanho real (100 x 60 mm), sem ajustar à página.")
    if st.button("Fechar", key=f"etiqueta_fechar_{pedido['id']}", use_container_width=True):
        st.rerun()
