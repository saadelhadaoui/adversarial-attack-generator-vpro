import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
<style>
#MainMenu, footer, [data-testid="stToolbar"] {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

:root {
  --bg: #050816;
  --panel: #0b1026;
  --panel2: #070b1f;
  --cyan: #00e5ff;
  --blue: #2f8cff;
  --green: #22c55e;
  --red: #ff4d4d;
  --orange: #f97316;
  --purple: #8b5cf6;
  --text: #eef7ff;
  --muted: #c2d0e6;
  --muted-strong: #d7e4f4;
}

html, body, [class*="css"] {
  font-family: Inter, "Segoe UI", system-ui, sans-serif;
  color: var(--text);
}

.stApp {
  background:
    radial-gradient(900px 700px at 10% 0%, rgba(0, 229, 255, .12), transparent 62%),
    radial-gradient(700px 500px at 72% 9%, rgba(139, 92, 246, .12), transparent 64%),
    linear-gradient(180deg, #040715 0%, #060a1c 100%);
}
.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(0, 229, 255, .045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 229, 255, .045) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 80%);
  z-index: 0;
}
.block-container {
  max-width: 1180px;
  padding-top: 1rem;
  padding-bottom: 5rem;
}

h1, h2, h3, h4 {letter-spacing: -0.01em; color: var(--text);}
p,
small,
label,
[data-testid="stCaptionContainer"],
[data-testid="stMarkdownContainer"] p {
  color: var(--muted-strong);
}

.topnav {
  position: sticky;
  top: .7rem;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: .85rem 1rem;
  border-radius: 16px;
  background: rgba(5, 8, 22, .82);
  border: 1px solid rgba(255, 255, 255, .07);
  backdrop-filter: blur(16px);
  box-shadow: 0 18px 50px rgba(0, 0, 0, .22);
}
.topnav .brand {
  display: flex;
  align-items: center;
  gap: .55rem;
  font-weight: 800;
  white-space: nowrap;
}
.topnav .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--cyan);
  box-shadow: 0 0 18px var(--cyan);
}
.topnav .links {display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;}
.topnav a {color: var(--muted-strong); text-decoration: none; font-size: .88rem;}
.topnav a:hover {color: var(--cyan);}
.topnav .status {
  color: #22ff88;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: .78rem;
  white-space: nowrap;
}

.section {margin: 4.8rem 0 1.4rem;}
.section-header {
  display: flex;
  align-items: center;
  gap: .75rem;
  margin-bottom: 1.2rem;
}
.num {
  color: var(--cyan);
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: .82rem;
  font-weight: 700;
}
.eyebrow, .pill {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(0, 229, 255, .45);
  background: rgba(0, 229, 255, .06);
  border-radius: 999px;
  padding: .28rem .75rem;
  color: var(--cyan);
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: .75rem;
  letter-spacing: .16em;
  text-transform: uppercase;
}
.section-title {
  font-size: 2.25rem;
  line-height: 1.1;
  font-weight: 850;
  color: var(--text);
}
.section-title strong, .accent {
  color: var(--cyan);
}
.section-sub {
  color: var(--muted-strong);
  max-width: 850px;
  line-height: 1.65;
  margin-top: .6rem;
}

.glass, .hero-card, .problem-panel, .threat-card, .agent-card, .loop-card, .memory-card, .arch-card, .metric-card {
  background: linear-gradient(160deg, rgba(11, 16, 38, .82), rgba(7, 11, 31, .58));
  border: 1px solid rgba(255, 255, 255, .075);
  border-radius: 16px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
}
.glass {padding: 1.25rem; margin-top: .9rem;}

.hero-card {
  margin-top: .7rem;
  padding: 3.5rem 2.6rem 3rem;
  min-height: 470px;
  border-color: rgba(0, 229, 255, .22);
  background:
    radial-gradient(700px 420px at 35% 20%, rgba(139, 92, 246, .20), transparent 70%),
    radial-gradient(700px 420px at 22% 90%, rgba(0, 229, 255, .14), transparent 70%),
    linear-gradient(160deg, rgba(11, 16, 38, .90), rgba(7, 11, 31, .74));
}
.hero-kicker {margin-bottom: 2rem;}
.hero-title {
  max-width: 620px;
  font-size: 3.2rem;
  line-height: 1.08;
  font-weight: 900;
  margin: 0;
  color: #dff8ff;
}
.hero-title span {color: var(--cyan);}
.hero-subtitle {
  margin-top: 1.9rem;
  font-size: 1.12rem;
  color: rgba(238, 247, 255, .82);
}
.hero-copy {
  max-width: 760px;
  line-height: 1.65;
  color: var(--muted-strong);
}
.hero-copy b:nth-child(1) {color: #ffb4b4;}
.hero-copy b:nth-child(2) {color: #aeefff;}
.hero-copy b:nth-child(3) {color: #d8c8ff;}
.hero-copy b:nth-child(4) {color: #b5f7c9;}
.hero-actions {
  display: flex;
  gap: .8rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}
.hero-btn {
  display: inline-flex;
  color: #03131c;
  background: linear-gradient(135deg, #20d6ff, #2f8cff);
  text-decoration: none;
  font-weight: 800;
  border-radius: 10px;
  padding: .85rem 1.1rem;
}
.hero-btn.secondary {
  color: var(--text);
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.10);
}
.hero-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: .9rem;
  margin-top: 2.2rem;
}
.hero-stat {
  padding: 1rem;
  border-radius: 12px;
  background: rgba(5, 8, 22, .42);
  border: 1px solid rgba(255, 255, 255, .07);
}
.hero-stat .label {
  color: var(--muted-strong);
  font-family: "JetBrains Mono", Consolas, monospace;
  letter-spacing: .18em;
  text-transform: uppercase;
  font-size: .68rem;
}
.hero-stat .value {
  color: var(--cyan);
  font-size: 1.45rem;
  font-weight: 850;
  margin-top: .45rem;
}

.problem-panel {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 2rem;
  padding: 1.5rem;
}
.chip-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .7rem;
  align-content: center;
}
.chip {
  border-radius: 999px;
  padding: .45rem .75rem;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: .76rem;
  border: 1px solid rgba(255,255,255,.12);
}
.chip.red {color: #ffb4b4; border-color: rgba(255,77,77,.45);}
.chip.orange {color: #fdba74; border-color: rgba(249,115,22,.45);}
.chip.cyan {color: var(--cyan); border-color: rgba(0,229,255,.45);}
.chip.green {color: #22ff88; border-color: rgba(34,197,94,.45);}
.threat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1.3rem;
}
.threat-card {
  position: relative;
  padding: 1.35rem;
  border-color: rgba(255, 77, 77, .25);
  background:
    radial-gradient(420px 220px at 40% 0%, rgba(255, 77, 77, .16), transparent 70%),
    rgba(11, 16, 38, .78);
}
.threat-head {display: flex; justify-content: space-between; gap: 1rem; align-items: center;}
.threat-title {font-weight: 850; font-size: 1.05rem;}
.threat-level {
  color: #ffb4b4;
  border: 1px solid rgba(255,77,77,.5);
  border-radius: 999px;
  padding: .22rem .5rem;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: .7rem;
}
.threat-desc {color: var(--muted-strong); line-height: 1.6; font-size: .94rem;}
.codebox {
  margin-top: .9rem;
  padding: .8rem;
  border-radius: 10px;
  background: rgba(0,0,0,.34);
  border: 1px dashed rgba(255,255,255,.10);
  color: #c8d3e5;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: .78rem;
}

.agent-grid {display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.1rem; margin-top: 1.5rem;}
.agent-card {
  min-height: 210px;
  padding: 1.5rem;
  overflow: hidden;
  position: relative;
}
.agent-card::before {
  content: "";
  position: absolute;
  width: 260px;
  height: 260px;
  top: -120px;
  right: -80px;
  border-radius: 50%;
  filter: blur(50px);
  opacity: .28;
  background: currentColor;
}
.agent-card.red {color: var(--red); border-color: rgba(255,77,77,.32);}
.agent-card.cyan {color: var(--cyan); border-color: rgba(0,229,255,.32);}
.agent-card.purple {color: var(--purple); border-color: rgba(139,92,246,.32);}
.agent-card.green {color: var(--green); border-color: rgba(34,197,94,.32);}
.agent-card .role {color: var(--muted-strong);}
.agent-card h3 {margin: .7rem 0 .35rem; color: var(--text);}
.agent-card p, .agent-card li {color: var(--muted-strong); line-height: 1.55;}

.loop-wrap {
  display: grid;
  grid-template-columns: 1fr .95fr;
  gap: 1rem;
  margin-top: 1.4rem;
}
.orbit-card {
  min-height: 380px;
  position: relative;
  overflow: hidden;
}
.orbit {
  position: absolute;
  inset: 42px;
  border: 1px dashed rgba(0,229,255,.22);
  border-radius: 50%;
}
.orbit-node {
  position: absolute;
  transform: translate(-50%, -50%);
  background: rgba(11,16,38,.95);
  border: 1px solid rgba(0,229,255,.35);
  border-radius: 999px;
  padding: .55rem .85rem;
  font-weight: 800;
  font-size: .82rem;
}
.timeline {
  padding: 1.5rem;
}
.timeline-row {
  border-left: 1px dashed rgba(0,229,255,.35);
  padding: 0 0 1.2rem 1.1rem;
  position: relative;
}
.timeline-row::before {
  content: "";
  position: absolute;
  left: -6px;
  top: 2px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--cyan);
  box-shadow: 0 0 18px var(--cyan);
}
.timeline-row small {color: var(--muted-strong); font-family: "JetBrains Mono", Consolas, monospace;}
.loop-steps {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: .8rem;
  margin-top: 1.5rem;
}
.loop-step {text-align: center; padding: 1rem; border-color: rgba(0,229,255,.24);}
.loop-step b {display: block; margin-bottom: .45rem;}
.feed {text-align: center; color: var(--cyan); font-family: "JetBrains Mono", Consolas, monospace; margin-top: .7rem;}

.memory-split, .arch-memory-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1.3rem;
}
.memory-card {padding: 1.45rem; border-color: rgba(0,229,255,.28);}
.memory-card.purple {border-color: rgba(139,92,246,.35);}
.memory-card h4 {margin: .65rem 0;}
.memory-list {display: grid; gap: .55rem; margin-top: 1rem;}
.memory-item {
  background: rgba(0,0,0,.25);
  border: 1px dashed rgba(255,255,255,.10);
  border-radius: 8px;
  padding: .65rem .75rem;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: .82rem;
}
.arch-state {
  padding: 1.3rem;
  border-color: rgba(0,229,255,.25);
}
.arch-state-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: .9rem; margin-top: .9rem;}
.arch-card {padding: 1rem;}
.arch-packages {display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin-top: 1.2rem;}
.arch-card .present {float: right; color: #22ff88;}

.metric-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin-top: 1rem;}
.metric-card {padding: 1rem;}
.metric-card .label {color: var(--cyan); font-family: "JetBrains Mono", Consolas, monospace; font-size: .72rem;}
.metric-card .name {font-weight: 850; margin-top: .35rem;}
.metric-card .desc {color: var(--muted-strong); font-size: .9rem; line-height: 1.55;}

.trace-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: .55rem;
  margin: .7rem 0 .9rem;
}
.trace-item {
  min-width: 0;
  padding: .65rem .7rem;
  border-radius: 10px;
  background: rgba(5, 8, 22, .46);
  border: 1px solid rgba(255, 255, 255, .075);
}
.trace-label {
  color: var(--muted-strong);
  font-size: .66rem;
  line-height: 1;
  text-transform: uppercase;
  letter-spacing: .08em;
  white-space: nowrap;
}
.trace-value {
  margin-top: .4rem;
  color: var(--text);
  font-size: .9rem;
  font-weight: 800;
  line-height: 1.15;
  overflow-wrap: anywhere;
}
.trace-value.good {color: #22ff88;}
.trace-value.bad {color: #ffb4b4;}
.trace-value.warn {color: #fdba74;}
.trace-value.info {color: var(--cyan);}
.trace-value.muted {color: var(--muted-strong);}

.pill.green {color: #22ff88; border-color: rgba(34,197,94,.45); background: rgba(34,197,94,.07);}
.pill.red {color: #ffb4b4; border-color: rgba(255,77,77,.45); background: rgba(255,77,77,.07);}
.pill.orange {color: #fdba74; border-color: rgba(249,115,22,.45); background: rgba(249,115,22,.07);}
.pill.purple {color: #c4b5fd; border-color: rgba(139,92,246,.45); background: rgba(139,92,246,.07);}
.pill.muted {color: var(--muted-strong); border-color: rgba(194,208,230,.38); background: rgba(194,208,230,.07);}
.console {
  background: #020611;
  border: 1px solid rgba(0,229,255,.20);
  border-radius: 14px;
  padding: 1rem;
  font-family: "JetBrains Mono", Consolas, monospace;
  max-height: 460px;
  overflow: auto;
}
.console .ln {display: block; margin: .28rem 0;}
.console .ts {color: #b6c5dc; margin-right: .7rem;}
.console .ok {color: #22ff88;} .console .bad {color: #ff4d4d;} .console .info {color: var(--cyan);} .console .warn {color: var(--orange);}

.stButton > button {
  min-height: 2.9rem;
  background: linear-gradient(135deg, #47e4ff 0%, #248bff 100%);
  color: #00111f !important;
  border: 0;
  border-radius: 10px;
  font-weight: 900;
  padding: .7rem 1rem;
  letter-spacing: 0;
  line-height: 1.15;
  text-shadow: 0 1px 0 rgba(255, 255, 255, .34);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.35), 0 10px 28px rgba(47,140,255,.18);
  white-space: normal;
}
.stButton > button p,
.stButton > button span {
  color: #00111f !important;
  font-weight: 900 !important;
  line-height: 1.15;
  opacity: 1 !important;
}
.stButton > button:hover {
  color: #00111f !important;
  filter: brightness(1.08);
  transform: translateY(-1px);
}
.stButton > button:focus,
.stButton > button:active {
  color: #00111f !important;
  border: 0;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.35), 0 0 0 2px rgba(0,229,255,.35);
}
.stTabs [data-baseweb="tab-list"] {gap: .35rem;}
.stTabs [data-baseweb="tab"] {
  background: rgba(11,16,38,.7);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 10px;
  color: var(--muted-strong);
}
.stTabs [aria-selected="true"] {color: var(--cyan) !important; border-color: rgba(0,229,255,.45) !important;}
.footer {
  margin-top: 3rem;
  padding: 1.2rem 0;
  text-align: center;
  color: var(--muted-strong);
  border-top: 1px solid rgba(255,255,255,.08);
}

@media (max-width: 980px) {
  .topnav {display: block;}
  .topnav .links {margin-top: .7rem;}
  .hero-title {font-size: 2.35rem;}
  .hero-stats, .threat-grid, .agent-grid, .loop-wrap, .memory-split, .arch-memory-grid, .arch-packages {
    grid-template-columns: 1fr;
  }
  .loop-steps {grid-template-columns: 1fr 1fr;}
  .problem-panel {grid-template-columns: 1fr;}
  .trace-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
}
</style>
""",
        unsafe_allow_html=True,
    )
