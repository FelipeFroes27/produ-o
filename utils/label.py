"""Etiqueta de produção (100 x 60 mm, 300 dpi) — gerada como PNG e PDF. O PDF tem
exatamente o tamanho da etiqueta, pronto pra imprimir sem escala.

No sistema as etiquetas são geradas em memória (`gerar_etiquetas`) e entregues
por download; `export_production_label` salva uma etiqueta avulsa em
'exportacoes/Etiquetas' (uso local, ex.: layout de exemplo)."""
from __future__ import annotations

import io
import re
import zlib
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_ICONES_DIR = Path(__file__).resolve().parent.parent / "icones"
_DPI = 300
_MM = _DPI / 25.4
_WIDTH, _HEIGHT = round(100 * _MM), round(60 * _MM)
_PAD = 28
_BAND = 138
_GRID_TOP = 410
_FUSO_BRASILIA = timezone(timedelta(hours=-3))
# Arial no Windows; no Linux (Streamlit Cloud) a Liberation Sans, que tem as mesmas medidas.
_FONTES_REGULAR = [
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
_FONTES_BOLD = [
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


@lru_cache(maxsize=None)
def _font(bold: bool, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for caminho in _FONTES_BOLD if bold else _FONTES_REGULAR:
        try:
            return ImageFont.truetype(caminho, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: float, start: int):
    size = start
    while size > 12 and draw.textlength(text, font=_font(True, size)) > max_width:
        size -= 1
    return _font(True, size)


def _logo(name: str, height: int) -> Image.Image | None:
    path = _ICONES_DIR / name
    if not path.exists():
        return None
    image = Image.open(path).convert("RGBA")
    return image.resize((round(image.width * height / image.height), height), Image.LANCZOS)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: float) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    return lines + [line] if line else lines


def formatar_ordem(ordem: str) -> str:
    """A ordem sai como 'OP 12345'; se o número vier sem o prefixo, acrescenta."""
    texto = " ".join(str(ordem or "").split())
    if not texto:
        return "-"
    if re.match(r"op\b", texto, flags=re.IGNORECASE):
        return texto
    return f"OP {texto}"


def render_production_label(
    codigo: str, descricao: str, ordem: str, quantidade: str, data_hora: str, responsavel: str,
) -> Image.Image:
    """Desenha a etiqueta: cabeçalho com os logos Goper/TrendX, código e descrição
    do produto (a descrição ocupa o maior tamanho de letra que couber, em até 3
    linhas) e uma grade 2x2 com ordem, quantidade, data/hora e responsável."""
    image = Image.new("RGB", (_WIDTH, _HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    # cabeçalho (os arquivos de logo são escuros sobre fundo branco)
    goper = _logo("Logo goper.png", 96)
    trendx = _logo("Logo Trendx.png", 50)
    left = _PAD + (goper.width if goper else 0)
    right = _WIDTH - _PAD - (trendx.width if trendx else 0)
    if goper:
        image.paste(goper, (_PAD, (_BAND - goper.height) // 2), goper)
    if trendx:
        image.paste(trendx, (right, (_BAND - trendx.height) // 2), trendx)
    title = "ETIQUETA DE PRODUÇÃO"
    title_font = _font(True, 36)
    draw.text((left + (right - left - draw.textlength(title, font=title_font)) / 2, _BAND / 2 - 22), title, font=title_font, fill="black")
    draw.line([_PAD, _BAND, _WIDTH - _PAD, _BAND], fill="black", width=6)

    # produto
    top = _BAND + 16
    draw.text((_PAD, top), "PRODUTO", font=_font(False, 26), fill="#555555")
    draw.text((_PAD, top + 22), codigo, font=_font(True, 80), fill="black")

    text_top = top + 112
    available = _GRID_TOP - 12 - text_top
    max_width = _WIDTH - 2 * _PAD
    descricao = " ".join(descricao.split())
    lines: list[str] = []
    description_font = _font(True, 28)
    size = 28
    for size in range(60, 27, -1):
        description_font = _font(True, size)
        lines = _wrap(draw, descricao, description_font, max_width)
        if len(lines) <= 3 and len(lines) * round(size * 1.12) <= available:
            break
    else:
        # nem no menor tamanho coube: corta em 3 linhas, com reticências na última
        lines = lines[:3]
        while lines and draw.textlength(lines[-1] + "…", font=description_font) > max_width:
            lines[-1] = lines[-1][:-1]
        if lines:
            lines[-1] += "…"
    for number, line in enumerate(lines):
        draw.text((_PAD, text_top + number * round(size * 1.12)), line, font=description_font, fill="black")

    # grade de informações (2 x 2)
    draw.line([_PAD, _GRID_TOP, _WIDTH - _PAD, _GRID_TOP], fill="black", width=3)
    cells = [("ORDEM", ordem), ("QUANTIDADE", quantidade), ("DATA / HORA", data_hora), ("RESPONSÁVEL", responsavel)]
    row_h = (_HEIGHT - _GRID_TOP - 8) // 2
    col_w = (_WIDTH - 2 * _PAD) / 2
    for index, (label, value) in enumerate(cells):
        cell_x = _PAD + (index % 2) * col_w
        cell_y = _GRID_TOP + (index // 2) * row_h
        draw.text((cell_x, cell_y + 12), label, font=_font(False, 26), fill="#555555")
        draw.text((cell_x, cell_y + 44), value, font=_fit_font(draw, value, col_w - 24, 64), fill="black")
    draw.line([_PAD, _GRID_TOP + row_h, _WIDTH - _PAD, _GRID_TOP + row_h], fill="black", width=3)
    draw.line([_PAD + col_w - 14, _GRID_TOP, _PAD + col_w - 14, _HEIGHT - 12], fill="black", width=3)

    draw.rectangle([0, 0, _WIDTH - 1, _HEIGHT - 1], outline="black", width=4)
    return image


def _montar_pdf(grupos: list[tuple[Image.Image, int]]) -> bytes:
    """PDF com uma página de exatamente 100 x 60 mm por etiqueta. `grupos` traz
    (imagem, cópias): cada imagem é gravada uma só vez e reaproveitada nas
    páginas repetidas, então um lote grande continua pequeno. A imagem vai sem
    perdas (Flate), o que mantém o texto nítido na impressão."""
    largura_pt = 100 / 25.4 * 72
    altura_pt = 60 / 25.4 * 72
    objetos: list[bytes] = [b"", b""]  # 1 = catálogo, 2 = lista de páginas (preenchidos no fim)

    def novo(corpo: bytes) -> int:
        objetos.append(corpo)
        return len(objetos)

    def fluxo(cabecalho: str, dados: bytes) -> bytes:
        return f"<< {cabecalho} /Length {len(dados)} >>\nstream\n".encode() + dados + b"\nendstream"

    imagens = []
    for imagem, _ in grupos:
        rgb = imagem.convert("RGB")
        dados = zlib.compress(rgb.tobytes(), 9)
        imagens.append(novo(fluxo(
            f"/Type /XObject /Subtype /Image /Width {rgb.width} /Height {rgb.height} "
            "/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode",
            dados,
        )))

    desenho = f"q {largura_pt:.4f} 0 0 {altura_pt:.4f} 0 0 cm /Im0 Do Q".encode()
    paginas: list[int] = []
    for (_, copias), numero_imagem in zip(grupos, imagens):
        for _ in range(copias):
            conteudo = novo(fluxo("", desenho))
            paginas.append(novo(
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {largura_pt:.4f} {altura_pt:.4f}] "
                f"/Resources << /XObject << /Im0 {numero_imagem} 0 R >> >> /Contents {conteudo} 0 R >>".encode()
            ))
    if not paginas:
        raise ValueError("Nenhuma etiqueta para gerar.")

    objetos[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objetos[1] = f"<< /Type /Pages /Kids [{' '.join(f'{n} 0 R' for n in paginas)}] /Count {len(paginas)} >>".encode()

    saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posicoes = []
    for numero, corpo in enumerate(objetos, start=1):
        posicoes.append(len(saida))
        saida += f"{numero} 0 obj\n".encode() + corpo + b"\nendobj\n"
    inicio_xref = len(saida)
    saida += f"xref\n0 {len(objetos) + 1}\n".encode() + b"0000000000 65535 f \n"
    saida += b"".join(f"{posicao:010d} 00000 n \n".encode() for posicao in posicoes)
    saida += f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF\n".encode()
    return bytes(saida)


def _png_bytes(imagem: Image.Image) -> bytes:
    buffer = io.BytesIO()
    imagem.save(buffer, "PNG", dpi=(_DPI, _DPI))
    return buffer.getvalue()


def gerar_etiquetas(codigo: str, descricao: str, itens: list[dict], quando: datetime | None = None) -> tuple[bytes, bytes, int]:
    """Gera uma etiqueta por unidade, em memória (nada é gravado em disco).

    `itens` é uma lista de {"ordem", "responsavel", "unidades"}: cada item gera
    `unidades` etiquetas "1 UN" com a sua ordem e o seu responsável. A data e a
    hora são as do momento da geração (horário de Brasília).

    Retorna (PDF com todas as etiquetas, PNG da primeira etiqueta, total)."""
    quando = quando or datetime.now(_FUSO_BRASILIA)
    data_hora = quando.strftime("%d/%m/%Y %H:%M")
    grupos: list[tuple[Image.Image, int]] = []
    for item in itens:
        copias = int(item["unidades"])
        if copias <= 0:
            continue
        imagem = render_production_label(
            str(codigo), str(descricao), formatar_ordem(item["ordem"]), "1 UN", data_hora, str(item["responsavel"]).upper(),
        )
        grupos.append((imagem, copias))
    if not grupos:
        raise ValueError("Nenhuma etiqueta para gerar.")
    return _montar_pdf(grupos), _png_bytes(grupos[0][0]), sum(copias for _, copias in grupos)


def _slug(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^\w\-]+", "-", text.strip(), flags=re.UNICODE)).strip("-") or "sem-ordem"


def export_production_label(
    codigo: str, descricao: str, ordem: str, quantidade: int, responsavel: str, exports_dir: Path,
) -> tuple[Path, Path]:
    """Gera uma etiqueta avulsa e salva PNG + PDF (100 x 60 mm) em
    'exportacoes/Etiquetas'. Retorna (caminho do PNG, caminho do PDF). Não grava
    nada nos arquivos de dados."""
    now = datetime.now(_FUSO_BRASILIA)
    image = render_production_label(
        codigo, descricao, formatar_ordem(ordem), f"{quantidade:,} UN".replace(",", "."), now.strftime("%d/%m/%Y %H:%M"), responsavel.upper(),
    )
    folder = exports_dir / "Etiquetas"
    folder.mkdir(parents=True, exist_ok=True)
    base = f"Etiqueta_{codigo}_{_slug(ordem)}_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
    png_path, pdf_path = folder / f"{base}.png", folder / f"{base}.pdf"
    image.save(png_path, dpi=(_DPI, _DPI))
    pdf_path.write_bytes(_montar_pdf([(image, 1)]))
    return png_path, pdf_path
