import html


def pill(text: str, variant: str = "muted") -> str:
    return f'<span class="pill {html.escape(variant)}">{html.escape(str(text))}</span>'


def metric_story_card(label: str, name: str, desc: str) -> str:
    return f"""
<div class="metric-card">
  <div class="label">{html.escape(label)}</div>
  <div class="name">{html.escape(name)}</div>
  <div class="desc">{html.escape(desc)}</div>
</div>
"""


def console_line(ts: str, kind: str, text: str) -> str:
    return f'<span class="ln"><span class="ts">{html.escape(ts)}</span><span class="{kind}">{html.escape(text)}</span></span>'


def console_block(lines: list[str]) -> str:
    return '<div class="console">' + "".join(lines) + "</div>"
