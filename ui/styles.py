import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
<style>
#MainMenu, footer, [data-testid="stToolbar"] {visibility: hidden;}
.stApp {
  background: linear-gradient(180deg, #050816 0%, #070b1f 100%);
  color: #e5e7eb;
}
.block-container {max-width: 1280px; padding-top: 1rem;}
.topnav {
  position: sticky; top: 0; z-index: 10; display: flex; justify-content: space-between;
  align-items: center; gap: 1rem; padding: .8rem 1rem; border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px; background: rgba(5,8,22,.85); backdrop-filter: blur(12px);
}
.topnav a {color: #94a3b8; text-decoration: none; margin-left: .8rem;}
.brand {font-weight: 700;}
.dot {display: inline-block; width: 10px; height: 10px; border-radius: 999px; background: #00e5ff; margin-right: .5rem;}
.section {margin-top: 3rem;}
.section-header {display: flex; align-items: center; gap: .7rem; margin-bottom: .4rem;}
.num {font-family: monospace; color: #00e5ff;}
.eyebrow, .pill {
  display: inline-block; border: 1px solid rgba(0,229,255,.35); border-radius: 999px;
  padding: .18rem .55rem; color: #00e5ff; font-size: .76rem; font-family: monospace;
}
.section-title {font-size: 2rem; font-weight: 800; color: #f8fafc;}
.section-sub {color: #94a3b8; max-width: 850px; line-height: 1.6;}
.glass, .metric-card {
  background: rgba(11,16,38,.76); border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px; padding: 1rem; margin-top: .8rem;
}
.metric-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin-top: 1rem;}
@media (max-width: 900px) {.metric-grid {grid-template-columns: 1fr;} .topnav {display: block;}}
.metric-card .label {color: #00e5ff; font-family: monospace; font-size: .75rem;}
.metric-card .name {font-weight: 700; margin-top: .3rem;}
.metric-card .desc {color: #94a3b8; font-size: .92rem; margin-top: .3rem;}
.pill.green {color: #22c55e; border-color: rgba(34,197,94,.35);}
.pill.red {color: #ff4d4d; border-color: rgba(255,77,77,.35);}
.pill.orange {color: #f97316; border-color: rgba(249,115,22,.35);}
.pill.purple {color: #c4b5fd; border-color: rgba(139,92,246,.35);}
.pill.muted {color: #94a3b8; border-color: rgba(148,163,184,.25);}
.console {background: #030712; border: 1px solid rgba(0,229,255,.18); border-radius: 12px; padding: 1rem; font-family: monospace;}
.console .ln {display: block; margin: .2rem 0;}
.console .ts {color: #64748b; margin-right: .6rem;}
.console .ok {color: #22c55e;} .console .bad {color: #ff4d4d;} .console .info {color: #00e5ff;} .console .warn {color: #f97316;}
.footer {margin-top: 3rem; padding: 1rem 0; color: #94a3b8; text-align: center; border-top: 1px solid rgba(255,255,255,.08);}
</style>
""",
        unsafe_allow_html=True,
    )
