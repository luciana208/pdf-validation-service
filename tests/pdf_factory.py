"""generador de pdfs validos en memoria para los tests (sin librerias externas)"""


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(pages: list[str] | None = None, padding: int = 0) -> bytes:
    """
    arma un pdf con una pagina por cada texto de `pages`; `padding` agrega un objeto
    de relleno para llegar a un tamaño dado. la tabla xref usa los offsets reales.
    """
    pages = pages if pages is not None else [""]
    kids = " ".join(f"{4 + 2 * index} 0 R" for index in range(len(pages)))
    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        f"<</Type/Pages/Kids[{kids}]/Count {len(pages)}>>".encode(),
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    for index, text in enumerate(pages):
        content_number = 5 + 2 * index
        objects.append(
            f"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents {content_number} 0 R"
            f"/Resources<</Font<</F1 3 0 R>>>>>>".encode()
        )
        stream = f"BT /F1 12 Tf 72 720 Td ({_escape(text)}) Tj ET".encode("latin-1") if text else b""
        objects.append(b"<</Length %d>>stream\n" % len(stream) + stream + b"\nendstream")
    if padding:
        objects.append(b"<</Length %d>>stream\n" % padding + b"0" * padding + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj" % number + body + b"endobj\n"
    xref_position = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    out += b"trailer<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF" % (len(objects) + 1, xref_position)
    return bytes(out)


TEXT_PDF = build_pdf(["Hola Mundo PDF"])
NOT_A_PDF = b"PK\x03\x04 esto es un zip renombrado"
CORRUPT_PDF = b"%PDF-1.4\nbasura que no es un pdf"
