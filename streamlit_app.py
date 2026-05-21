from __future__ import annotations

import streamlit as st

from ui.agents_section import render_agents_section
from ui.architecture_section import render_architecture_section
from ui.chatbot_arena import render_chatbot_arena, render_chatbot_results_section
from ui.evaluation_section import render_evaluation_section
from ui.evidence_section import render_evidence_section
from ui.final_section import render_final_section
from ui.hero import render_hero
from ui.layout import render_footer, render_page_selector, render_top_nav
from ui.loop_section import render_loop_section
from ui.memory_section import render_memory_section
from ui.problem import render_problem_section
from ui.simulation_section import render_simulation_section
from ui.styles import inject_global_styles


def configure_page() -> None:
    st.set_page_config(
        page_title="Adaptive Multi-Agent LLM Defense Lab",
        page_icon="shield",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def main() -> None:
    configure_page()
    inject_global_styles()
    render_top_nav()
    page = render_page_selector()
    if page == "Chatbot Arena":
        render_chatbot_arena()
    elif page == "Results":
        render_chatbot_results_section()
        render_simulation_section()
        render_evidence_section()
        render_memory_section()
        render_evaluation_section()
    else:
        render_hero()
        render_problem_section()
        render_agents_section()
        render_loop_section()
        render_architecture_section()
        render_final_section()
    render_footer()


if __name__ == "__main__":
    main()
