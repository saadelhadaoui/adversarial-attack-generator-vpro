from __future__ import annotations

import html
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
OUT_DIR = ROOT / "reports"
ASSET_DIR = OUT_DIR / "pptx_assets"
PPTX_PATH = OUT_DIR / "Adaptive_Multi_Agent_LLM_Defense_Lab.pptx"

SLIDE_W, SLIDE_H = 1920, 1080
PPT_CX, PPT_CY = 12192000, 6858000

BG = (5, 8, 22)
BG2 = (9, 15, 36)
CYAN = (0, 229, 255)
BLUE = (47, 140, 255)
GREEN = (32, 255, 125)
RED = (255, 77, 77)
ORANGE = (255, 170, 64)
WHITE = (240, 247, 255)
MUTED = (170, 185, 210)
CARD = (12, 19, 44)
LINE = (0, 210, 255)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


F_TITLE = font(64, True)
F_H1 = font(48, True)
F_H2 = font(34, True)
F_BODY = font(26)
F_SMALL = font(20)
F_TINY = font(16)
F_MONO = font(20)


def fit_text(draw: ImageDraw.ImageDraw, text: str, max_width: int, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    while size >= 14:
        f = font(size, bold)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_width:
            return f
        size -= 2
    return font(14, bold)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int] = WHITE,
    max_width: int = 800,
    line_gap: int = 8,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y


def gradient_bg() -> Image.Image:
    img = Image.new("RGB", (SLIDE_W, SLIDE_H), BG)
    px = img.load()
    for y in range(SLIDE_H):
        for x in range(SLIDE_W):
            gx = int(16 * x / SLIDE_W)
            gy = int(28 * y / SLIDE_H)
            purple = int(22 * max(0, (x - 1050)) / 870)
            px[x, y] = (BG[0] + gx // 5, BG[1] + gy // 6, BG[2] + gx + purple)
    overlay = Image.new("RGBA", (SLIDE_W, SLIDE_H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(0, SLIDE_W, 80):
        od.line((x, 0, x, SLIDE_H), fill=(0, 190, 255, 18), width=1)
    for y in range(0, SLIDE_H, 80):
        od.line((0, y, SLIDE_W, y), fill=(0, 190, 255, 13), width=1)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], outline=LINE, fill=CARD, radius=24, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, color=CYAN, fill=(8, 25, 44)):
    x, y = xy
    f = F_TINY
    tw = draw.textbbox((0, 0), text, font=f)[2]
    box = (x, y, x + tw + 34, y + 34)
    draw.rounded_rectangle(box, radius=17, fill=fill, outline=color, width=1)
    draw.text((x + 17, y + 8), text, font=f, fill=color)


def add_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str | None = None, number: str | None = None):
    y = 62
    if number:
        pill(draw, (90, y), number, CYAN)
        y += 56
    draw.text((90, y), title, font=F_H1, fill=WHITE)
    draw.line((90, y + 65, 90 + min(760, len(title) * 26), y + 65), fill=CYAN, width=4)
    if subtitle:
        draw_wrapped(draw, (90, y + 88), subtitle, F_BODY, MUTED, 1200)


def open_img(name: str) -> Image.Image:
    return Image.open(SCREENSHOTS / name).convert("RGB")


def place_image(
    base: Image.Image,
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 20,
    border: tuple[int, int, int] = LINE,
    shadow: bool = True,
):
    x1, y1, x2, y2 = box
    max_w, max_h = x2 - x1, y2 - y1
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    px, py = x1 + (max_w - nw) // 2, y1 + (max_h - nh) // 2
    resized = img.resize((nw, nh), Image.LANCZOS)

    if shadow:
        sh = Image.new("RGBA", (nw + 32, nh + 32), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((16, 16, nw + 16, nh + 16), radius=radius, fill=(0, 0, 0, 125))
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        base.paste(sh, (px - 16, py - 10), sh)

    mask = Image.new("L", (nw, nh), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, nw, nh), radius=radius, fill=255)
    base.paste(resized, (px, py), mask)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((px, py, px + nw, py + nh), radius=radius, outline=border, width=2)


def slide_title() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    logo = open_img("logo-vert.png")
    lab = open_img("WhatsApp Image 2026-05-15 at 13.20.45.jpeg")
    place_image(img, logo, (120, 82, 760, 380), radius=12, border=(30, 80, 70), shadow=False)
    place_image(img, lab, (1270, 76, 1790, 402), radius=12, border=(30, 80, 70), shadow=False)
    d.text((120, 480), "Adaptive Multi-Agent", font=F_TITLE, fill=WHITE)
    d.text((120, 552), "LLM Defense Lab", font=F_TITLE, fill=CYAN)
    d.line((120, 642, 1060, 642), fill=CYAN, width=5)
    draw_wrapped(
        d,
        (120, 690),
        "Adaptive AI Security Through Agentic Defense, Live SQLite Memory, Ollama, and Controlled Demonstration",
        F_H2,
        WHITE,
        1260,
    )
    card(d, (120, 870, 1110, 960), outline=CYAN, fill=(8, 20, 39), radius=18)
    d.text((160, 898), "Streamlit UI  |  Ollama LLM  |  SQLite Memory  |  Multi-Agent Orchestration", font=F_BODY, fill=WHITE)
    d.text((120, 1004), "Final technical presentation", font=F_SMALL, fill=MUTED)
    return img


def slide_overview() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Project Overview", "A live AI security lab that detects, evaluates, learns, and adapts from adversarial prompts.", "01")
    bullets = [
        ("Defender", "Classifies input and chooses PASS, BLOCK, REFORMULATE, or monitored execution."),
        ("Protected Chatbot", "Uses Ollama for normal replies and synthetic outputs for safe demos."),
        ("Evaluator", "Scores whether the defense succeeded and whether a synthetic leak occurred."),
        ("Learner + Memory", "Stores patterns, rules, RAG events, and interactions in SQLite."),
    ]
    y = 260
    for label, desc in bullets:
        card(d, (95, y, 805, y + 112), outline=(0, 130, 155), fill=(8, 20, 43), radius=18)
        d.text((125, y + 22), label, font=F_BODY, fill=CYAN)
        draw_wrapped(d, (300, y + 22), desc, F_SMALL, MUTED, 455, 5)
        y += 130
    place_image(img, open_img("Screenshot 2026-05-15 130530.png"), (900, 230, 1810, 940), radius=24)
    return img


def slide_architecture() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "System Architecture", "Every interaction moves through a closed feedback loop: defense, response, evaluation, learning, and memory.", "02")
    labels = [
        ("User / Prompt", 130, 365, BLUE),
        ("Defender Agent", 455, 365, CYAN),
        ("Protected Chatbot", 780, 365, GREEN),
        ("Evaluator Agent", 1105, 365, ORANGE),
        ("Learning Agent", 780, 650, CYAN),
        ("SQLite Memory", 455, 650, (190, 135, 255)),
    ]
    for text, x, y, color in labels:
        card(d, (x, y, x + 250, y + 92), outline=color, fill=(10, 21, 45), radius=18)
        f = fit_text(d, text, 205, 24, True)
        tw = d.textbbox((0, 0), text, font=f)[2]
        d.text((x + (250 - tw) // 2, y + 31), text, font=f, fill=WHITE)
    arrows = [((380, 411), (455, 411)), ((705, 411), (780, 411)), ((1030, 411), (1105, 411)), ((1230, 457), (930, 650)), ((780, 696), (705, 696)), ((580, 650), (580, 457))]
    for a, b in arrows:
        d.line((*a, *b), fill=CYAN, width=4)
        d.ellipse((b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6), fill=CYAN)
    place_image(img, open_img("Screenshot 2026-05-15 131115.png"), (1290, 250, 1830, 875), radius=24)
    return img


def slide_agents() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Agent Design", "Four cooperating agents turn single chatbot defense into an adaptive system.", "03")
    place_image(img, open_img("Screenshot 2026-05-15 131001.png"), (120, 280, 1800, 1000), radius=24)
    return img


def slide_arena() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Interactive Arena", "The presenter can switch mode, send prompts, run scripted tests, and inspect the trace.", "04")
    place_image(img, open_img("Screenshot 2026-05-15 130622.png"), (90, 285, 1810, 1010), radius=24)
    return img


def slide_demo_flow() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Controlled Demonstration Flow", "The safe demo shows a first monitored breach, learning, then repeat blocking.", "05")
    steps = [
        ("1", "Reset learned memory", "Start from a fresh database state."),
        ("2", "First controlled attempt", "Allow monitored synthetic leak for evidence."),
        ("3", "Evaluator flags success", "Defense score drops and attack success is recorded."),
        ("4", "Repeat attempt", "Learned memory blocks the pattern."),
    ]
    x = 90
    for num, title, desc in steps:
        card(d, (x, 260, x + 405, 435), outline=CYAN, fill=(8, 21, 45), radius=22)
        d.ellipse((x + 28, 292, x + 82, 346), fill=(0, 60, 90), outline=CYAN, width=2)
        d.text((x + 47, 305), num, font=F_BODY, fill=CYAN)
        d.text((x + 105, 292), title, font=F_BODY, fill=WHITE)
        draw_wrapped(d, (x + 105, 332), desc, F_SMALL, MUTED, 250, 4)
        x += 445
    place_image(img, open_img("Screenshot 2026-05-15 130638.png"), (120, 500, 945, 1005), radius=24)
    place_image(img, open_img("Screenshot 2026-05-15 130712.png"), (985, 500, 1810, 1005), radius=24)
    return img


def slide_pipeline() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Live Pipeline Evidence", "The simulation log and summary metrics are generated from SQLite rows.", "06")
    place_image(img, open_img("Screenshot 2026-05-15 131031.png"), (90, 285, 1810, 1010), radius=24)
    return img


def slide_memory() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Persistent SQLite Memory", "The learner stores reusable patterns and the UI reads memory tables live.", "07")
    place_image(img, open_img("Screenshot 2026-05-15 131059.png"), (95, 285, 1810, 1010), radius=24)
    return img


def slide_evaluation() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Evaluation Metrics", "Defense score, attack success, false positives, and latest rows are computed from recorded history.", "08")
    place_image(img, open_img("Screenshot 2026-05-15 131250.png"), (85, 285, 930, 1010), radius=24)
    place_image(img, open_img("Screenshot 2026-05-15 131259.png"), (980, 315, 1815, 925), radius=24)
    return img


def slide_takeaway() -> Image.Image:
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    add_title(d, "Final Takeaway", "A safe public demonstration of adaptive LLM defense.", "09")
    left = [
        ("Protection Mode", "Blocks suspicious prompt injection, jailbreak, and data exfiltration attempts."),
        ("Controlled Mode", "Allows monitored synthetic events only to prove learning and adaptation."),
        ("Live Memory", "SQLite records interactions, learned patterns, rules, RAG events, and metrics."),
        ("Ready to Present", "Ollama + Streamlit + multi-agent backend are connected for live demo."),
    ]
    y = 250
    for title, desc in left:
        d.rectangle((120, y + 10, 128, y + 86), fill=CYAN)
        d.text((155, y), title, font=F_H2, fill=WHITE)
        draw_wrapped(d, (155, y + 46), desc, F_BODY, MUTED, 770, 6)
        y += 150
    place_image(img, open_img("Screenshot 2026-05-15 131044.png"), (1050, 250, 1810, 780), radius=24)
    card(d, (1050, 830, 1810, 955), outline=GREEN, fill=(8, 26, 36), radius=22)
    d.text((1090, 862), "Core message", font=F_BODY, fill=GREEN)
    draw_wrapped(d, (1090, 902), "The defense does not only reject attacks. It observes, evaluates, remembers, and improves.", F_SMALL, WHITE, 660, 5)
    return img


def save_slides() -> list[Path]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    slides = [
        slide_title(),
        slide_overview(),
        slide_architecture(),
        slide_agents(),
        slide_arena(),
        slide_demo_flow(),
        slide_pipeline(),
        slide_memory(),
        slide_evaluation(),
        slide_takeaway(),
    ]
    paths: list[Path] = []
    for i, slide in enumerate(slides, 1):
        path = ASSET_DIR / f"slide_{i:02d}.png"
        slide.save(path, "PNG")
        paths.append(path)
    return paths


def xml_escape(value: str) -> str:
    return html.escape(value, quote=True)


def slide_xml(slide_num: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:pic>
        <p:nvPicPr>
          <p:cNvPr id="2" name="Slide {slide_num}"/>
          <p:cNvPicPr/>
          <p:nvPr/>
        </p:nvPicPr>
        <p:blipFill>
          <a:blip r:embed="rId2"/>
          <a:stretch><a:fillRect/></a:stretch>
        </p:blipFill>
        <p:spPr>
          <a:xfrm>
            <a:off x="0" y="0"/>
            <a:ext cx="{PPT_CX}" cy="{PPT_CY}"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        </p:spPr>
      </p:pic>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""


def slide_rels(slide_num: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/slide_{slide_num:02d}.png"/>
</Relationships>
"""


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
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{slide_overrides}
</Types>
"""


def presentation_xml(slide_count: int) -> str:
    ids = "\n".join(
        f'    <p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
{ids}
  </p:sldIdLst>
  <p:sldSz cx="{PPT_CX}" cy="{PPT_CY}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>
"""


def presentation_rels(slide_count: int) -> str:
    rels = ['  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    for i in range(1, slide_count + 1):
        rels.append(f'  <Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{chr(10).join(rels)}
</Relationships>
"""


def package_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def app_xml(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex Generated Presentation</Application>
  <PresentationFormat>Widescreen</PresentationFormat>
  <Slides>{slide_count}</Slides>
  <Company>EMSI</Company>
</Properties>
"""


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{xml_escape("Adaptive Multi-Agent LLM Defense Lab")}</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def slide_master_xml() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="050816"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>
"""


def slide_master_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""


def slide_layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>
"""


def slide_layout_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""


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
</a:theme>
"""


def make_pptx(slide_paths: list[Path]):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PPTX_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slide_paths)))
        z.writestr("_rels/.rels", package_rels())
        z.writestr("docProps/app.xml", app_xml(len(slide_paths)))
        z.writestr("docProps/core.xml", core_xml())
        z.writestr("ppt/presentation.xml", presentation_xml(len(slide_paths)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slide_paths)))
        z.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels())
        z.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels())
        z.writestr("ppt/theme/theme1.xml", theme_xml())
        for i, slide_path in enumerate(slide_paths, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(i))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels(i))
            z.write(slide_path, f"ppt/media/slide_{i:02d}.png")


def main():
    slide_paths = save_slides()
    make_pptx(slide_paths)
    print(PPTX_PATH)


if __name__ == "__main__":
    main()
