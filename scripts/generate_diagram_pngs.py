from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "diagrams"

BG = "#fffdf9"
INK = "#23313f"
BOX = "#f8f5ef"
ACCENT = "#d9efe3"
WARN = "#f7e2d6"


def font(size: int):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", size)
    except Exception:
        return ImageFont.load_default()


FONT = font(24)
SMALL = font(18)


def box(draw: ImageDraw.ImageDraw, xy, text: str, fill=BOX, text_font=FONT):
    draw.rounded_rectangle(xy, radius=18, fill=fill, outline=INK, width=3)
    x0, y0, x1, y1 = xy
    bbox = draw.multiline_textbbox((0, 0), text, font=text_font, spacing=4, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.multiline_text(
        ((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2 - 2),
        text,
        fill=INK,
        font=text_font,
        spacing=4,
        align="center",
    )


def arrow(draw: ImageDraw.ImageDraw, start, end):
    draw.line([start, end], fill=INK, width=4)
    ex, ey = end
    if abs(end[0] - start[0]) >= abs(end[1] - start[1]):
        sign = 1 if end[0] > start[0] else -1
        draw.polygon([(ex, ey), (ex - 16 * sign, ey - 8), (ex - 16 * sign, ey + 8)], fill=INK)
    else:
        sign = 1 if end[1] > start[1] else -1
        draw.polygon([(ex, ey), (ex - 8, ey - 16 * sign), (ex + 8, ey - 16 * sign)], fill=INK)


def architecture():
    img = Image.new("RGB", (1800, 980), BG)
    d = ImageDraw.Draw(img)
    layout = {
        "docs": (60, 210, 290, 330, "Input\nDocuments", BOX),
        "ingest": (360, 210, 680, 330, "Multi-Parser\nIngestion", ACCENT),
        "norm": (750, 210, 1080, 330, "Evidence Atom\nNormalizer", BOX),
        "graph": (1150, 210, 1460, 330, "Evidence Graph\nBuilder", BOX),
        "index": (1520, 210, 1740, 330, "Index\nManager", BOX),
        "query": (520, 630, 800, 750, "Query Router", ACCENT),
        "program": (880, 630, 1180, 750, "Context Program", BOX),
        "retrieve": (1460, 40, 1780, 160, "Graph + Semantic\nRetrieval", BOX),
        "gen": (1460, 430, 1780, 550, "Generator /\nExtractor", BOX),
        "verify": (1460, 630, 1780, 750, "Verification\nEngine", ACCENT),
        "reproc": (1010, 820, 1350, 940, "Selective Reprocessing", WARN),
        "output": (1460, 820, 1780, 940, "Answer / JSON /\nEvidence Trace", BOX),
    }
    for x0, y0, x1, y1, text, fill in layout.values():
        box(d, (x0, y0, x1, y1), text, fill=fill)
    d.text((150, 665), "Task Input / Query", fill=INK, font=FONT)
    arrow(d, (290, 270), (360, 270))
    arrow(d, (680, 270), (750, 270))
    arrow(d, (1080, 270), (1150, 270))
    arrow(d, (1460, 270), (1520, 270))
    arrow(d, (1620, 160), (1620, 210))
    arrow(d, (430, 690), (520, 690))
    arrow(d, (800, 690), (880, 690))
    d.line([(1180, 690), (1360, 690), (1360, 490), (1460, 490)], fill=INK, width=4)
    d.polygon([(1460, 490), (1444, 482), (1444, 498)], fill=INK)
    arrow(d, (1630, 330), (1630, 430))
    arrow(d, (1630, 550), (1630, 630))
    arrow(d, (1630, 750), (1630, 820))
    d.text((1360, 785), "Support weak?", fill=INK, font=SMALL)
    arrow(d, (1460, 880), (1350, 880))
    d.text((1388, 850), "Yes", fill=INK, font=SMALL)
    d.line([(1010, 880), (860, 880), (860, 330)], fill=INK, width=4)
    d.polygon([(860, 330), (852, 346), (868, 346)], fill=INK)
    d.text((1660, 785), "No", fill=INK, font=SMALL)
    img.save(OUT / "architecture.png")


def process_flow():
    img = Image.new("RGB", (1200, 1940), BG)
    d = ImageDraw.Draw(img)
    steps = [
        "Receive document",
        "Run OCR, layout,\nVLM, and table parsers",
        "Normalize parser outputs\ninto evidence atoms",
        "Add metadata:\ncoordinates, role,\nconfidence, provenance",
        "Construct evidence graph",
        "Build semantic,\nstructural, and spatial indexes",
        "Receive task input",
        "Predict task type and\nevidence requirements",
        "Generate context program",
        "Retrieve and traverse\nevidence graph",
        "Generate answer\nor extraction",
    ]
    y = 50
    centers = []
    for step in steps:
        xy = (280, y, 860, y + 94)
        box(d, xy, step)
        centers.append(((xy[0] + xy[2]) // 2, (xy[1] + xy[3]) // 2))
        y += 136
    arrow_x = 570
    for i in range(len(centers) - 1):
        top = 50 + i * 136
        arrow(d, (arrow_x, top + 94), (arrow_x, 50 + (i + 1) * 136))
    diamond = [(570, 1568), (740, 1660), (570, 1752), (400, 1660)]
    d.polygon(diamond, fill=ACCENT, outline=INK)
    d.text((462, 1643), "Adequate support?", fill=INK, font=SMALL)
    arrow(d, (570, 1410), (570, 1568))
    box(d, (790, 1608, 1070, 1702), "Reprocess uncertain\nregions", fill=WARN)
    arrow(d, (740, 1660), (790, 1660))
    d.text((752, 1630), "No", fill=INK, font=SMALL)
    d.line([(930, 1608), (930, 742), (860, 742)], fill=INK, width=4)
    d.polygon([(860, 742), (876, 734), (876, 750)], fill=INK)
    box(d, (280, 1790, 860, 1884), "Return supported output", fill=BOX)
    arrow(d, (570, 1752), (570, 1790))
    d.text((595, 1770), "Yes", fill=INK, font=SMALL)
    img.save(OUT / "process_flow.png")


def data_model():
    img = Image.new("RGB", (1700, 1080), BG)
    d = ImageDraw.Draw(img)
    items = {
        "Document": (60, 60, 390, 270, ["id", "metadata", "source_uri"]),
        "Page": (500, 60, 830, 270, ["page_number", "width", "height"]),
        "ParserRun": (940, 60, 1300, 270, ["parser_type", "parser_version", "confidence_profile"]),
        "EvidenceAtom": (520, 390, 940, 730, ["atom_id", "atom_type", "content", "coordinates", "reading_order", "confidence", "role_label"]),
        "Edge": (1080, 430, 1380, 650, ["edge_type", "weight"]),
        "ContextProgram": (60, 760, 430, 1010, ["task_type", "traversal_policy", "ranking_policy", "verification_policy"]),
        "SupportSubgraph": (560, 800, 980, 1010, ["support_score", "consistency_score", "provenance_score"]),
    }
    for title, (x0, y0, x1, y1, fields) in items.items():
        d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=BOX, outline=INK, width=3)
        d.rounded_rectangle((x0, y0, x1, y0 + 44), radius=18, fill=ACCENT, outline=INK, width=3)
        d.text((x0 + 18, y0 + 10), title, fill=INK, font=FONT)
        fy = y0 + 70
        for field in fields:
            d.text((x0 + 18, fy), field, fill=INK, font=SMALL)
            fy += 32
    d.text((200, 30), "Structural source objects", fill=INK, font=SMALL)
    d.text((1030, 360), "Graph relationships", fill=INK, font=SMALL)
    d.text((180, 725), "Retrieval and verification control", fill=INK, font=SMALL)
    arrow(d, (390, 165), (500, 165))
    d.text((425, 130), "contains", fill=INK, font=SMALL)
    arrow(d, (665, 270), (665, 390))
    d.text((685, 320), "yields", fill=INK, font=SMALL)
    d.line([(1120, 270), (1120, 330), (820, 390)], fill=INK, width=4)
    d.polygon([(820, 390), (836, 382), (836, 398)], fill=INK)
    d.text((1030, 300), "provenance", fill=INK, font=SMALL)
    arrow(d, (940, 560), (1080, 560))
    d.text((980, 520), "linked by", fill=INK, font=SMALL)
    arrow(d, (430, 885), (560, 885))
    d.text((450, 850), "supports", fill=INK, font=SMALL)
    arrow(d, (770, 800), (770, 730))
    d.text((790, 760), "grounds", fill=INK, font=SMALL)
    img.save(OUT / "data_model.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    architecture()
    process_flow()
    data_model()
    print(OUT)


if __name__ == "__main__":
    main()
