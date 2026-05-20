from __future__ import annotations

import html
import itertools
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
OUT_DIR = ROOT / "reports"
PPTX_PATH = OUT_DIR / "Adaptive_Multi_Agent_LLM_Defense_Lab_EDITABLE.pptx"

PPT_CX, PPT_CY = 12192000, 6858000
EMU_PER_IN = 914400

NAVY = "050816"
NAVY2 = "0A1024"
CYAN = "00E5FF"
BLUE = "2F8CFF"
GREEN = "20FF7D"
RED = "FF4D4D"
ORANGE = "F97316"
PURPLE = "8B5CF6"
WHITE = "F3F7FF"
MUTED = "B5C2D8"
CARD = "0B1430"
BLACK = "000000"


def emu(value: float) -> int:
    return int(value * EMU_PER_IN)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def rgb(color: str) -> str:
    return color.replace("#", "").upper()


class Slide:
    def __init__(self, title: str = ""):
        self.title = title
        self.parts: list[str] = []
        self.rels: list[tuple[str, str, str]] = []
        self.media: list[tuple[Path, str]] = []
        self._id = itertools.count(2)
        self._rid = itertools.count(2)

    def next_id(self) -> int:
        return next(self._id)

    def add_bg(self):
        self.rect(0, 0, 13.333, 7.5, NAVY, NAVY, 0, name="Background")
        for x in [i / 2 for i in range(0, 28)]:
            self.rect(x, 0, 0.006, 7.5, "0B2340", "0B2340", 0, transparency=55000, name="Grid V")
        for y in [i / 2 for i in range(0, 16)]:
            self.rect(0, y, 13.333, 0.006, "0B2340", "0B2340", 0, transparency=65000, name="Grid H")

    def title_block(self, number: str, title: str, subtitle: str | None = None):
        self.pill(0.62, 0.42, number, CYAN, 0.38, 0.22, font_size=10)
        self.text(0.62, 0.83, 6.5, 0.45, title, 30, WHITE, bold=True, name="Slide Title")
        self.rect(0.62, 1.33, min(3.8, 0.22 * len(title)), 0.035, CYAN, CYAN, 0, name="Title Underline")
        if subtitle:
            self.text(0.62, 1.52, 8.8, 0.34, subtitle, 15, MUTED, name="Subtitle")

    def text(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        value: str,
        font_size: int = 16,
        color: str = WHITE,
        bold: bool = False,
        name: str = "Text",
        fill: str | None = None,
        line: str | None = None,
        radius: bool = False,
        margin: int = 91440,
    ):
        shape_id = self.next_id()
        geom = "roundRect" if radius else "rect"
        fill_xml = '<a:noFill/>' if fill is None else solid_fill(fill)
        line_xml = '<a:ln><a:noFill/></a:ln>' if line is None else f'<a:ln w="12700">{solid_fill(line)}</a:ln>'
        paragraphs = "\n".join(
            f"""<a:p><a:r><a:rPr lang="en-US" sz="{font_size * 100}" b="{1 if bold else 0}">{solid_fill(color)}<a:latin typeface="Arial"/></a:rPr><a:t>{esc(line_text)}</a:t></a:r><a:endParaRPr lang="en-US" sz="{font_size * 100}"/></a:p>"""
            for line_text in value.split("\n")
        )
        self.parts.append(
            f"""<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
    {fill_xml}
    {line_xml}
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square" anchor="t" lIns="{margin}" tIns="{margin}" rIns="{margin}" bIns="{margin}"/>
    <a:lstStyle/>
    {paragraphs}
  </p:txBody>
</p:sp>"""
        )

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        line: str,
        radius: int = 0,
        transparency: int | None = None,
        name: str = "Rectangle",
    ):
        shape_id = self.next_id()
        geom = "roundRect" if radius else "rect"
        fill_xml = solid_fill(fill, transparency)
        line_xml = f'<a:ln w="12700">{solid_fill(line, transparency)}</a:ln>'
        self.parts.append(
            f"""<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
    <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
    {fill_xml}
    {line_xml}
  </p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
</p:sp>"""
        )

    def pill(self, x: float, y: float, value: str, color: str, w: float, h: float, font_size: int = 9):
        self.text(x, y, w, h, value, font_size, color, True, fill=NAVY2, line=color, radius=True, margin=40000, name="Pill")

    def card(self, x: float, y: float, w: float, h: float, title: str, body: str, color: str = CYAN):
        self.rect(x, y, w, h, CARD, color, radius=1, transparency=None, name=f"{title} Card")
        self.text(x + 0.18, y + 0.18, w - 0.36, 0.32, title, 16, WHITE, True, name=f"{title} Title")
        self.text(x + 0.18, y + 0.58, w - 0.36, h - 0.74, body, 11, MUTED, name=f"{title} Body")

    def image(self, img_path: Path, x: float, y: float, w: float, h: float, name: str = "Image"):
        actual = img_path
        if not actual.exists():
            raise FileNotFoundError(actual)
        with Image.open(actual) as im:
            iw, ih = im.size
        box_ratio = w / h
        img_ratio = iw / ih
        if img_ratio > box_ratio:
            final_w = w
            final_h = w / img_ratio
        else:
            final_h = h
            final_w = h * img_ratio
        final_x = x + (w - final_w) / 2
        final_y = y + (h - final_h) / 2
        rid = f"rId{next(self._rid)}"
        ext = actual.suffix.lower().lstrip(".")
        safe_slide = "".join(ch if ch.isalnum() else "_" for ch in self.title)[:24]
        safe_stem = "".join(ch if ch.isalnum() else "_" for ch in actual.stem)[:28]
        media_name = f"{safe_slide}_{len(self.media) + 1}_{safe_stem}.{ext}"
        self.media.append((actual, media_name))
        self.rels.append((rid, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", f"../media/{media_name}"))
        shape_id = self.next_id()
        self.parts.append(
            f"""<p:pic>
  <p:nvPicPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
  <p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
  <p:spPr>
    <a:xfrm><a:off x="{emu(final_x)}" y="{emu(final_y)}"/><a:ext cx="{emu(final_w)}" cy="{emu(final_h)}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:ln w="12700">{solid_fill(CYAN, 20000)}</a:ln>
  </p:spPr>
</p:pic>"""
        )

    def arrow(self, x1: float, y1: float, x2: float, y2: float, color: str = CYAN):
        shape_id = self.next_id()
        self.parts.append(
            f"""<p:cxnSp>
  <p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="Arrow"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
  <p:spPr>
    <a:xfrm><a:off x="{emu(min(x1, x2))}" y="{emu(min(y1, y2))}"/><a:ext cx="{emu(abs(x2 - x1))}" cy="{emu(abs(y2 - y1))}"/></a:xfrm>
    <a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>
    <a:ln w="25400">{solid_fill(color)}<a:tailEnd type="none"/><a:headEnd type="triangle"/></a:ln>
  </p:spPr>
</p:cxnSp>"""
        )

    def xml(self) -> str:
        body = "\n".join(self.parts)
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {body}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""

    def rels_xml(self) -> str:
        rels = [('rId1', "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "../slideLayouts/slideLayout1.xml")]
        rels.extend(self.rels)
        body = "\n".join(f'  <Relationship Id="{rid}" Type="{typ}" Target="{esc(target)}"/>' for rid, typ, target in rels)
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{body}
</Relationships>"""


def solid_fill(color: str, transparency: int | None = None) -> str:
    alpha = "" if transparency is None else f"<a:alpha val=\"{100000 - transparency}\"/>"
    return f'<a:solidFill><a:srgbClr val="{rgb(color)}">{alpha}</a:srgbClr></a:solidFill>'


def screenshot(name: str) -> Path:
    return SCREENSHOTS / name


def build_slides() -> list[Slide]:
    slides: list[Slide] = []

    s = Slide("Title")
    s.add_bg()
    s.image(screenshot("logo-vert.png"), 0.65, 0.55, 4.9, 1.75, "EMSI Logo")
    s.image(screenshot("WhatsApp Image 2026-05-15 at 13.20.45.jpeg"), 9.6, 0.55, 2.45, 1.9, "EMSI Student Lab Logo")
    s.text(0.75, 3.05, 7.4, 0.55, "Adaptive Multi-Agent", 40, WHITE, True)
    s.text(0.75, 3.68, 7.4, 0.62, "LLM Defense Lab", 40, CYAN, True)
    s.rect(0.75, 4.42, 6.45, 0.04, CYAN, CYAN)
    s.text(0.75, 4.78, 8.6, 0.75, "Adaptive AI Security Through Agentic Defense, Live SQLite Memory, Ollama, and Controlled Demonstration", 22, WHITE, True)
    s.text(0.75, 6.18, 6.95, 0.52, "Streamlit UI  |  Ollama LLM  |  SQLite Memory  |  Multi-Agent Orchestration", 16, WHITE, fill=NAVY2, line=CYAN, radius=True)
    slides.append(s)

    s = Slide("Project Overview")
    s.add_bg()
    s.title_block("01", "Project Overview", "A live AI security lab that detects, evaluates, learns, and adapts from adversarial prompts.")
    s.card(0.65, 2.15, 4.65, 0.82, "Defender", "Classifies input and chooses PASS, BLOCK, REFORMULATE, or monitored execution.", CYAN)
    s.card(0.65, 3.15, 4.65, 0.82, "Protected Chatbot", "Uses Ollama for normal replies and synthetic outputs for safe demos.", GREEN)
    s.card(0.65, 4.15, 4.65, 0.82, "Evaluator", "Scores defense success, attack success, and false positives.", ORANGE)
    s.card(0.65, 5.15, 4.65, 0.82, "Learner + Memory", "Stores patterns, generated rules, RAG events, and interactions in SQLite.", PURPLE)
    s.image(screenshot("Screenshot 2026-05-15 130530.png"), 5.85, 1.95, 6.95, 4.85, "Main UI")
    slides.append(s)

    s = Slide("System Architecture")
    s.add_bg()
    s.title_block("02", "System Architecture", "A closed feedback loop connects input, defense, chatbot response, evaluation, learning, and memory.")
    boxes = [
        ("User / Prompt", 0.9, 2.8, BLUE),
        ("Defender Agent", 3.2, 2.8, CYAN),
        ("Protected Chatbot", 5.5, 2.8, GREEN),
        ("Evaluator Agent", 7.8, 2.8, ORANGE),
        ("Learning Agent", 5.5, 4.65, CYAN),
        ("SQLite Memory", 3.2, 4.65, PURPLE),
    ]
    for label, x, y, color in boxes:
        s.text(x, y, 1.75, 0.62, label, 14, WHITE, True, fill=CARD, line=color, radius=True, margin=55000)
    s.arrow(2.65, 3.1, 3.18, 3.1)
    s.arrow(4.95, 3.1, 5.48, 3.1)
    s.arrow(7.25, 3.1, 7.78, 3.1)
    s.arrow(8.66, 3.42, 6.45, 4.65)
    s.arrow(5.5, 4.96, 4.95, 4.96)
    s.arrow(4.08, 4.65, 4.08, 3.42)
    s.text(9.6, 2.15, 2.75, 2.9, "Memory gives the Defender context about previous attacks.\n\nThe Evaluator turns outcomes into scores.\n\nThe Learner converts failures into reusable rules.", 15, WHITE, fill=NAVY2, line=CYAN, radius=True)
    s.image(screenshot("Screenshot 2026-05-15 131115.png"), 8.95, 5.15, 3.7, 1.5, "Architecture UI")
    slides.append(s)

    s = Slide("Agent Design")
    s.add_bg()
    s.title_block("03", "Agent Design", "Four specialized agents cooperate to make the chatbot adaptive instead of static.")
    s.card(0.75, 2.15, 2.95, 1.3, "Attacker Agent", "Generates safe synthetic probes for presentation and testing.", RED)
    s.card(3.95, 2.15, 2.95, 1.3, "Defender Agent", "Classifies prompt risk and applies mode-aware policy.", CYAN)
    s.card(7.15, 2.15, 2.95, 1.3, "Evaluator Agent", "Audits the result and records scores in SQLite.", PURPLE)
    s.card(10.35, 2.15, 2.25, 1.3, "Learning Agent", "Stores patterns and generated rules.", GREEN)
    s.image(screenshot("Screenshot 2026-05-15 131001.png"), 1.0, 3.85, 11.4, 2.55, "Agent Section")
    slides.append(s)

    s = Slide("Interactive Arena")
    s.add_bg()
    s.title_block("04", "Interactive Arena", "Switch modes, run prompts, inspect traces, and show the live defense decision.")
    s.image(screenshot("Screenshot 2026-05-15 130622.png"), 0.75, 1.95, 11.85, 4.95, "Chatbot Arena")
    s.text(0.9, 6.95, 11.25, 0.34, "Protection mode blocks suspicious prompts. Controlled mode allows monitored synthetic events to prove adaptation.", 15, GREEN, True)
    slides.append(s)

    s = Slide("Controlled Demo Flow")
    s.add_bg()
    s.title_block("05", "Controlled Demo Flow", "A first controlled attack can be allowed under monitoring, learned, then blocked when repeated.")
    steps = [
        ("1", "Reset Memory", "Fresh database state."),
        ("2", "First Attempt", "Monitored synthetic leak."),
        ("3", "Learning", "Pattern saved to SQLite."),
        ("4", "Repeat", "Same pattern is blocked."),
    ]
    for i, (num, title, body) in enumerate(steps):
        x = 0.65 + i * 3.15
        s.text(x, 2.0, 2.65, 0.9, f"{num}  {title}\n{body}", 14, WHITE, True, fill=CARD, line=CYAN, radius=True)
    s.image(screenshot("Screenshot 2026-05-15 130638.png"), 0.75, 3.25, 5.9, 2.8, "First Attempt")
    s.image(screenshot("Screenshot 2026-05-15 130712.png"), 6.75, 3.25, 5.8, 2.8, "Repeat Attempt")
    slides.append(s)

    s = Slide("Live Pipeline Evidence")
    s.add_bg()
    s.title_block("06", "Live Pipeline Evidence", "The log, summary, and chart are read from real SQLite interaction rows.")
    s.image(screenshot("Screenshot 2026-05-15 131031.png"), 0.65, 1.95, 8.0, 4.95, "Pipeline Log")
    s.text(9.05, 2.1, 3.25, 1.0, "What the audience sees", 20, CYAN, True, fill=NAVY2, line=CYAN, radius=True)
    s.text(9.05, 3.25, 3.25, 2.4, "• Defender actions\n• Risk and defense scores\n• Attack success rate\n• Learned patterns\n• Real-time refresh", 17, WHITE, fill=CARD, line=CYAN, radius=True)
    slides.append(s)

    s = Slide("SQLite Memory")
    s.add_bg()
    s.title_block("07", "SQLite Memory", "Memory is not decorative: the UI reads learned patterns, rules, RAG events, and interactions live.")
    s.image(screenshot("Screenshot 2026-05-15 131059.png"), 0.7, 1.9, 8.15, 4.95, "Memory UI")
    s.card(9.15, 2.05, 3.05, 0.92, "Interactions", "Every prompt and decision is logged.", CYAN)
    s.card(9.15, 3.15, 3.05, 0.92, "Learned Patterns", "Successful attacks become memory.", GREEN)
    s.card(9.15, 4.25, 3.05, 0.92, "Defender Rules", "Generated rules influence future decisions.", PURPLE)
    s.card(9.15, 5.35, 3.05, 0.92, "RAG Events", "Retrieval makes past attacks visible.", ORANGE)
    slides.append(s)

    s = Slide("Evaluation Metrics")
    s.add_bg()
    s.title_block("08", "Evaluation Metrics", "Evaluation balances safety and usefulness instead of simply blocking everything.")
    s.image(screenshot("Screenshot 2026-05-15 131250.png"), 0.65, 1.95, 5.95, 4.95, "Evaluation Charts")
    s.image(screenshot("Screenshot 2026-05-15 131259.png"), 6.9, 2.05, 5.65, 3.35, "Evaluation Rows")
    s.text(6.9, 5.75, 5.65, 0.75, "Key metrics: interactions, attack success, defense success, average defense score, false positives, and learned patterns.", 16, WHITE, fill=CARD, line=CYAN, radius=True)
    slides.append(s)

    s = Slide("Final Takeaway")
    s.add_bg()
    s.title_block("09", "Final Takeaway", "The system demonstrates adaptive LLM defense in a safe, synthetic, presentation-ready way.")
    s.card(0.85, 2.05, 3.65, 1.05, "Protection Mode", "Blocks suspicious injection, jailbreak, and data exfiltration attempts.", CYAN)
    s.card(0.85, 3.35, 3.65, 1.05, "Controlled Mode", "Allows monitored synthetic events only for proof of learning.", ORANGE)
    s.card(0.85, 4.65, 3.65, 1.05, "Live Memory", "SQLite stores interactions, patterns, rules, RAG events, and metrics.", GREEN)
    s.image(screenshot("Screenshot 2026-05-15 131044.png"), 5.15, 2.0, 7.1, 3.35, "Evidence")
    s.text(5.15, 5.75, 7.1, 0.74, "Core message: the defense observes, evaluates, remembers, and improves after risky interactions.", 18, WHITE, True, fill=NAVY2, line=GREEN, radius=True)
    slides.append(s)

    s = Slide("Tools and References")
    s.add_bg()
    s.title_block("10", "Tools and References", "Main tools used to build and demonstrate the project.")
    s.text(0.8, 2.1, 5.8, 3.1, "Tools\n• Python\n• Streamlit\n• SQLite\n• Ollama\n• qwen2.5:14b-instruct-q4_K_M\n• Plotly\n• Multi-agent orchestration", 18, WHITE, fill=CARD, line=CYAN, radius=True)
    s.text(6.9, 2.1, 5.4, 3.1, "References\n• Ollama local LLM runtime documentation\n• Streamlit documentation\n• SQLite documentation\n• OWASP LLM application security guidance\n• Project source code and screenshots", 18, WHITE, fill=CARD, line=CYAN, radius=True)
    s.text(0.8, 6.15, 11.4, 0.45, "Adaptive Multi-Agent LLM Defense Lab - Final Technical Presentation", 18, CYAN, True)
    slides.append(s)

    return slides


def content_types(slide_count: int) -> str:
    slide_overrides = "\n".join(
        f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Default Extension="jpg" ContentType="image/jpeg"/>
  <Default Extension="jpeg" ContentType="image/jpeg"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{slide_overrides}
</Types>"""


def package_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def presentation_xml(slide_count: int) -> str:
    ids = "\n".join(f'    <p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, slide_count + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>
{ids}
  </p:sldIdLst>
  <p:sldSz cx="{PPT_CX}" cy="{PPT_CY}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels(slide_count: int) -> str:
    rels = ['  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    for i in range(1, slide_count + 1):
        rels.append(f'  <Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{chr(10).join(rels)}
</Relationships>"""


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Adaptive Multi-Agent LLM Defense Lab</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def app_xml(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>Codex Generated Editable Presentation</Application>
  <PresentationFormat>Widescreen</PresentationFormat>
  <Slides>{slide_count}</Slides>
  <Company>EMSI</Company>
</Properties>"""


def master_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def master_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def layout_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


def theme_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="DefenseLab">
  <a:themeElements>
    <a:clrScheme name="DefenseLab">
      <a:dk1><a:srgbClr val="050816"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="111827"/></a:dk2><a:lt2><a:srgbClr val="E5E7EB"/></a:lt2>
      <a:accent1><a:srgbClr val="00E5FF"/></a:accent1><a:accent2><a:srgbClr val="2F8CFF"/></a:accent2>
      <a:accent3><a:srgbClr val="20FF7D"/></a:accent3><a:accent4><a:srgbClr val="FF4D4D"/></a:accent4>
      <a:accent5><a:srgbClr val="F97316"/></a:accent5><a:accent6><a:srgbClr val="8B5CF6"/></a:accent6>
      <a:hlink><a:srgbClr val="2F8CFF"/></a:hlink><a:folHlink><a:srgbClr val="8B5CF6"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="DefenseLab"><a:majorFont><a:latin typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Arial"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="DefenseLab"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def make_pptx(slides: list[Slide]):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PPTX_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides)))
        z.writestr("_rels/.rels", package_rels())
        z.writestr("docProps/core.xml", core_xml())
        z.writestr("docProps/app.xml", app_xml(len(slides)))
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        z.writestr("ppt/slideMasters/slideMaster1.xml", master_xml())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels())
        z.writestr("ppt/slideLayouts/slideLayout1.xml", layout_xml())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels())
        z.writestr("ppt/theme/theme1.xml", theme_xml())
        media_written: set[str] = set()
        for idx, slide in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{idx}.xml", slide.xml())
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide.rels_xml())
            for source, media_name in slide.media:
                target = f"ppt/media/{media_name}"
                if target not in media_written:
                    z.write(source, target)
                    media_written.add(target)


def main():
    slides = build_slides()
    make_pptx(slides)
    print(PPTX_PATH)


if __name__ == "__main__":
    main()
